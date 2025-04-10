import pygame


class FloatingText:
    def __init__(self, text, player, game_resources, duration=2000):
        self.text = text
        self.player = player
        self.game_resources = game_resources
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.color = (255, 50, 0)
        self.offset_y = -50
        self.alpha = 255

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.creation_time

        # Fade out
        if elapsed > self.duration * 0.7:
            fade_time = self.duration * 0.3
            self.alpha = max(0, 255 * (1 - (elapsed - self.duration * 0.7) / fade_time))

        return elapsed < self.duration

    def draw(self, surface, camera_offset=None):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        pos_x = self.player.rect.centerx - camera_offset.x
        pos_y = self.player.rect.top - camera_offset.y + self.offset_y

        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        text_rect = text_surface.get_rect(center=(pos_x, pos_y))

        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_color = (0, 0, 0, int(self.alpha * 0.7))
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=5)

        surface.blit(bg_surface, bg_rect)
        surface.blit(text_surface, text_rect)
