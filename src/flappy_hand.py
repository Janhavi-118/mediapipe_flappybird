import mediapipe as mp
import cv2
import asyncio
import sys
import pygame
import numpy as np
from threading import Thread

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT
import tkinter as tk



class Flappy:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        screen_info = pygame.display.Info()
        self.screen_height = screen_info.current_h
        self.screen_width = screen_info.current_w
        self.ratio = self.screen_height/1024
        print(self.ratio)
        window = Window(576*self.ratio, self.screen_height)
        ##pygame.display.set_window_position(screen_width, 0)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=40,
            window=window,
            images=images,
            sounds=Sounds(),
        )

        self.hand_thread = Thread(target=self.hand_window)
        self.hand_thread.daemon = True
        self.hand_thread.start()

    

    async def start(self):
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            await self.splash()
            await self.play()
            await self.game_over()

    def hand_window(self):
        mp_holistic = mp.solutions.holistic
        holistic = mp_holistic.Holistic()
        mp_drawing = mp.solutions.drawing_utils

        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, self.frame = cap.read()
            if not ret:
                break
            self.frame_h, self.frame_w, _ = self.frame.shape
            self.frame = self.resize_with_aspect_ratio(self.frame, int(self.screen_width - (576*self.ratio)), int(self.screen_height))
            
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)

            if results.pose_landmarks and results.right_hand_landmarks:
                frame_height, frame_width, _ = self.frame.shape
                thumb = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
                self.thumb_coords = [int(thumb.x * frame_width), int(thumb.y * frame_height)]
                
                right_arm_connections = [
                    (mp_holistic.PoseLandmark.RIGHT_SHOULDER, mp_holistic.PoseLandmark.RIGHT_ELBOW),
                    (mp_holistic.PoseLandmark.RIGHT_ELBOW, mp_holistic.PoseLandmark.RIGHT_WRIST),
                    (mp_holistic.PoseLandmark.RIGHT_WRIST, mp_holistic.HandLandmark.THUMB_TIP)
                ]
                right_shoulder = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
                right_elbow = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_ELBOW]
                right_wrist = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST]

                self.shoulder_coords = [int(right_shoulder.x * frame_width), int(right_shoulder.y * frame_height)]
                self.elbow_coords = [int(right_elbow.x * frame_width), int(right_elbow.y * frame_height)]
                self.wrist_coords = [int(right_wrist.x * frame_width), int(right_wrist.y * frame_height)]
        
                i = 0 
                for connection in right_arm_connections:
                    start_idx, end_idx = connection
                    start_point = results.pose_landmarks.landmark[start_idx]
                    if i != 2:
                        end_point = results.pose_landmarks.landmark[end_idx]
                    elif i == 2:
                        end_point = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]

                    frame_height, frame_width, _ = self.frame.shape
                    start_coordinates = (int(start_point.x * frame_width), int(start_point.y * frame_height))
                    end_coordinates = (int(end_point.x * frame_width), int(end_point.y * frame_height))
                    
                    cv2.line(self.frame, start_coordinates, end_coordinates, (0, 255, 0), 2)
                    cv2.circle(self.frame, start_coordinates, 4, (0, 255, 0), -1)
                    cv2.circle(self.frame, end_coordinates, 4, (0, 255, 0), -1)
                    i = i + 1

            self.frame = cv2.flip(self.frame, 1)
            cv2.imshow('MediaPipe Holistic', self.frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = (self.frame_h, self.frame_w)

        if width is None and height is None:
            return image

        if height is None:
            r = width / float(w)
            dim = (width, int(h * r))
            
        else:
            r = height / float(h)
            dim = (int(w * r), height)

        resized = cv2.resize(image, dim, interpolation=inter)
        return resized


    def arm_straight(self):
        elbow_angle = self.calculate_angle(self.shoulder_coords, self.elbow_coords, self.wrist_coords)
        wrist_angle = self.calculate_angle(self.elbow_coords, self.wrist_coords, self.thumb_coords)
        
        if (elbow_angle >= 120 and wrist_angle >= 120 and elbow_angle <= 240 and wrist_angle <= 240):
            return True
        else:
            return False

    def calculate_angle(self, point1, point2, point3):
        p1 = np.array([point1[0], point1[1]])
        p2 = np.array([point2[0], point2[1]])
        p3 = np.array([point3[0], point3[1]])
        
        vector1 = p1 - p2
        vector2 = p3 - p2
        
        angle = np.arccos(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))
        angle = np.degrees(angle)
        
        return angle

    async def splash(self):
        self.player.set_mode(PlayerMode.SHM)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap
    
    async def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()
                    
            for event in pygame.event.get():
                self.check_quit_event(event)

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            if self.arm_straight():
                frame_height, _ = self.frame.shape[:2]
                hand_y = self.wrist_coords[1]  # Use wrist y-coordinate
                game_height = self.config.window.height
                player_y = (hand_y / frame_height) * game_height
                self.player.set_y(player_y)
            self.player.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)


    