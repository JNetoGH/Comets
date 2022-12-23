import pygame

from engine_JNeto_Productions.components.rect_trigger_component import RectTriggerComponent
from engine_JNeto_Productions.components.single_sprite_component import SingleSpriteComponent
from engine_JNeto_Productions.game_object_base_class import GameObject
from engine_JNeto_Productions.systems.scalable_game_screen_system import GameScreen


class Button(GameObject):

    def __init__(self, path_normal, path_active, position: pygame.Vector2, scale, func, scene, rendering_layer):
        super().__init__("menu_button", scene, rendering_layer)
        self.remove_default_rect_image()


        self.transform.move_world_position(position)
        self.fix_game_object_on_screen(position)

        self.path_normal = path_normal
        self.path_active = path_active
        self.single_sprite = SingleSpriteComponent(self.path_normal, self)
        self.scale = scale

        self.single_sprite.scale_itself(self.scale)

        self.rect_trigger = RectTriggerComponent(0, 0, self.image.get_width(), self.image.get_height(), self)

        self.func = func

        self._is_active = True

    def deactivate(self):
        self._is_active = False
        self.stop_rendering_this_game_object()

    def activate(self):
        self._is_active = True
        self.start_rendering_this_game_object()

    def game_object_update(self) -> None:

        if not self._is_active:
            return

        if self.rect_trigger.is_there_overlap_with_point(pygame.Vector2(pygame.mouse.get_pos())):
            self.single_sprite.change_image(self.path_active)
            self.single_sprite.scale_itself(self.scale)
            if pygame.mouse.get_pressed(3)[0]:
                self.func()
        else:
            self.single_sprite.change_image(self.path_normal)
            self.single_sprite.scale_itself(self.scale)
