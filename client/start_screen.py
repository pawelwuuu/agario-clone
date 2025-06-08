import pygame
import config

nick = ""

def show_start_screen(screen):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(config.WIDTH // 2 - 100, config.HEIGHT // 2 - 20, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    button_rect = pygame.Rect(config.WIDTH // 2 - 50, config.HEIGHT // 2 + 40, 100, 40)
    button_color = pygame.Color('green')
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive
                if button_rect.collidepoint(event.pos):
                    nick = text.strip()
                    done = True
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    nick = text.strip()
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 16:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        btn_text = font.render("Join", True, (255, 255, 255))
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(btn_text, (button_rect.x + 20, button_rect.y + 5))

        pygame.display.flip()
    
    return nick
