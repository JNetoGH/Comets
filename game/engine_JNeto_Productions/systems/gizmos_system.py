from typing import Union
import pygame

from engine_JNeto_Productions.components.circle_trigger_component import CircleTriggerComponent
from engine_JNeto_Productions.components.rect_collider_component import ColliderComponent
from engine_JNeto_Productions.components.rect_trigger_component import RectTriggerComponent
from engine_JNeto_Productions.systems.scalable_game_screen_system import GameScreen


class GizmosSystem:

    def __init__(self):

        # current scene
        self._current_scene = None

        # Descriptions
        path_to_font = 'engine_JNeto_Productions/_engine_resources/fonts/JetBrainsMono-Medium.ttf'
        self._FONT_SIZE = 15
        self._font = pygame.font.Font(path_to_font, self._FONT_SIZE)

        # Creating new surface every frame is too expensive, so, I try to cache all the gizmos surfaces
        self._cached_text_surfaces = {}

    def set_current_scene(self, scene):
        self._current_scene = scene

    def render_scene_game_objects_gizmos(self):
        if self._current_scene is None:
            return

        # game objects gizmos
        for gm_obj in self._current_scene.game_object_list:
            self._render_gizmos_of_game_obj_image_rect(gm_obj, pygame.Color("red"))
            if gm_obj.has_collider:
                self._render_gizmos_of_game_obj_colliders(gm_obj, pygame.Color("yellow"))
            if gm_obj.has_rect_trigger:
                self._render_gizmos_of_game_obj_rect_triggers(gm_obj, pygame.Color("green"))
            if gm_obj.has_circle_trigger:
                self._render_gizmos_of_game_obj_circle_triggers(gm_obj, pygame.Color("green"))
            if gm_obj.transform.is_center_point_appearing_on_screen_read_only:
                self._render_gizmos_of_game_obj_transform(gm_obj, pygame.Color("white"))

    def _get_cached_surface_or_cache_new_one(self, msg, color: pygame.Color) -> pygame.Surface:
        if msg not in self._cached_text_surfaces:
            self._cached_text_surfaces[msg] = self._font.render(msg, True, color).convert_alpha()
        return self._cached_text_surfaces[msg]

    def _render_text(self, text: str, position: pygame.Vector2, color: pygame.Color):
        text_surface = self._get_cached_surface_or_cache_new_one(text, color)
        GameScreen.GameScreenDummySurface.blit(text_surface, position)

    # ==================================================================================================================
    #                                                  TRANSFORM
    # ==================================================================================================================

    def _render_gizmos_of_game_obj_transform(self, gm_obj, color: pygame.Color) -> None:

        object_screen_pos = gm_obj.transform.screen_position_read_only

        # render the point
        pygame.draw.circle(GameScreen.GameScreenDummySurface, color, object_screen_pos, 5)

        # render description
        text = f"{gm_obj.name}'s TransformComponent"
        text_position = pygame.Vector2(object_screen_pos.x + 30, object_screen_pos.y - self._FONT_SIZE + 3)
        self._render_text(text, text_position, color)

    # ==================================================================================================================
    #                                             IMAGE RECTANGLE
    # ==================================================================================================================

    def _render_gizmos_of_game_obj_image_rect(self, game_obj, color: pygame.Color) -> None:

        object_screen_pos = game_obj.transform.screen_position_read_only

        # render the rect
        pygame.draw.rect(GameScreen.GameScreenDummySurface, color, game_obj.image_rect, 1)

        # render description
        text = f"{game_obj.name}'s image_rect"
        text_position = pygame.Vector2(0, 0)
        text_position.x = object_screen_pos[0] - game_obj.image_rect.width // 2
        text_position.y = object_screen_pos[1] - game_obj.image_rect.height // 2 - self._FONT_SIZE * 2
        self._render_text(text, text_position, color)

    # ==================================================================================================================
    #                                          RECTANGLE TRIGGERS/COLLIDERS
    # ==================================================================================================================

    def _render_gizmos_of_game_obj_colliders(self, game_obj, color: pygame.Color) -> None:
        # COLLIDERS GIZMOS
        for component in game_obj.components_list:
            if isinstance(component, ColliderComponent):
                # render component
                self._render_rect_of_rect_based_component(component, color)

    def _render_gizmos_of_game_obj_rect_triggers(self, game_obj, color: pygame.Color):
        # RECT TRIGGER GIZMOS
        for component in game_obj.components_list:
            if isinstance(component, RectTriggerComponent) and not isinstance(component, ColliderComponent):
                # render component
                self._render_rect_of_rect_based_component(component, color)

    def _render_rect_of_rect_based_component(self, component: Union[ColliderComponent, RectTriggerComponent], color: pygame.Color):

        game_obj = component.game_object_owner_read_only

        # THE REPRESENTATION OF THE COLLIDER/RECT TRIGGER AT SCREEN POSITION
        # the position of the collider/rect trigger is at world position,
        # so I have to treat its position for correct representation on screen
        representative_rect = component.inner_rect_read_only.copy()
        representative_rect.centerx = game_obj.transform.screen_position_read_only.x + component.offset_from_game_object_x
        representative_rect.centery = game_obj.transform.screen_position_read_only.y + component.offset_from_game_object_y

        # render the rect
        pygame.draw.rect(GameScreen.GameScreenDummySurface, color, representative_rect, 1)

        # renders the middle circle
        pygame.draw.circle(GameScreen.GameScreenDummySurface, color, representative_rect.center, 5)

        # render description
        text = f"{game_obj.name}'s {component.__class__.__name__}\n"
        text_position = pygame.Vector2()
        text_position.x = representative_rect.centerx + 30
        if isinstance(component, RectTriggerComponent) and not isinstance(component, ColliderComponent):
            text_position.y = representative_rect.centery - self._FONT_SIZE * 2
        else:
            text_position.y = representative_rect.centery + self._FONT_SIZE // 2
        self._render_text(text, text_position, color)

    # ==================================================================================================================
    #                                                   CIRCLE TRIGGERS
    # ==================================================================================================================

    def _render_gizmos_of_game_obj_circle_triggers(self, gm_obj, color):
        for component in gm_obj.components_list:
            if isinstance(component, CircleTriggerComponent):
                # THE REPRESENTATION OF THE CIRCLE TRIGGER AT SCREEN POSITION
                # the position of the trigger is at world position,
                # so I have to treat its position for correct representation on screen
                representative_circle_x = gm_obj.transform.screen_position_read_only.x + component.offset_from_game_object_x
                representative_circle_y = gm_obj.transform.screen_position_read_only.y + component.offset_from_game_object_y
                circle_center = pygame.Vector2(representative_circle_x, representative_circle_y)
                pygame.draw.circle(GameScreen.GameScreenDummySurface, color, circle_center, component.radius, 1)

                # render description
                text = f"{gm_obj.name}'s {component.__class__.__name__}\n"
                text_position = pygame.Vector2()
                text_position.x = circle_center.x + 30
                text_position.y = circle_center.y - self._FONT_SIZE * 2
                self._render_text(text, text_position, color)
