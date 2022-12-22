import enum
import pygame
from engine_JNeto_Productions.components.circle_trigger_component import CircleTriggerComponent
from engine_JNeto_Productions.components.single_sprite_component import SingleSpriteComponent
from engine_JNeto_Productions.components.timer_component import TimerComponent
from engine_JNeto_Productions.game_object_base_class import GameObject
from engine_JNeto_Productions.systems.file_manager_system import FileManager
from engine_JNeto_Productions.systems.game_time_system import GameTime
from game_object_score_scene.score_registration_floating_menu import ScoreRegistrationFloatingMenu
from game_objects_main_scene.game_object_bullet import Bullet
from game_objects_main_scene.game_object_player import Player
from game_objects_main_scene.game_object_score import Score


class Meteor(GameObject):

    Game_loop = None
    Score_scene = None

    class MeteorRank(enum.Enum):
        Small = 1
        Mid = 2
        Big = 4

    def __init__(self, scene, rank: MeteorRank, initial_position: pygame.Vector2, direction: pygame.Vector2):
        super().__init__("meteor", scene, scene.camera.get_rendering_layer_by_name("over_player_layer"))

        # scales the meteor to its ranks value
        self.sigle_sprite = SingleSpriteComponent("game_res/meteor.png", self)
        self.sigle_sprite.scale_itself(rank.value)

        # circle trigger
        self.circle_trigger = CircleTriggerComponent(0,0, self.image.get_width()//2, self)

        # lifetime
        # 20
        self.life_time_is_seg = 20
        self.life_time_timer = TimerComponent(self.life_time_is_seg*1000, self, self._set_to_garbage_collection)
        self.life_time_timer.activate()

        # moves to initial position
        self.transform.move_world_position(initial_position)

        # move and direction
        # 100
        self.move_speed = 100
        self.direction = direction

        # rank: related to size and instantiation of other meteors post-death
        self.rank = rank

        # player and score
        self.player: Player = self.scene.get_game_object_by_name("player")
        self.score: Score = self.scene.get_game_object_by_name("score")

    def game_object_update(self) -> None:

        # move
        self.move_to_direction()

        # checks for collisions with bullets, if killed, create the lower rank ones
        for bullet in Bullet.In_Scene_Bullets:
            if self.circle_trigger.is_there_overlap_with_point(bullet.transform.world_position_read_only):
                # removes bullet from scene
                bullet.set_bullet_to_garbage_collection()
                # instantiates the sub ranks and gives the points to the player
                self._instantiate_sub_ranks_if_possible()
                # removes itself from scene
                self._set_to_garbage_collection()

        # player hit
        if self.circle_trigger.is_there_overlap_with_rect(self.player.player_collider.inner_rect_read_only):

            csv = FileManager.read_from_csv_file("game_data/score_sheet.csv")

            total_amount_registered = len(csv)
            last_guy_index = 10 if total_amount_registered >= 10 else total_amount_registered-1
            pontuacao_do_ultimo = int(csv[last_guy_index][1])

            managed_to_get_in_the_ranking_sheet = self.score.score_points_read_only > pontuacao_do_ultimo

            print(f"managed to get in the rank: {managed_to_get_in_the_ranking_sheet}\n"
                  f"points: {self.score.score_points_read_only}\n"
                  f"10th points: {pontuacao_do_ultimo}\n")

            if managed_to_get_in_the_ranking_sheet:
                ScoreRegistrationFloatingMenu.TotalPoints = self.score.score_points_read_only
                ScoreRegistrationFloatingMenu.Show = True
            else:
                ScoreRegistrationFloatingMenu.TotalPoints = 0
                ScoreRegistrationFloatingMenu.Show = False

            # sends to score scene
            Meteor.Game_loop.set_current_scene(Meteor.Score_scene)

    def _instantiate_sub_ranks_if_possible(self):
        # instantiates the sub rank comets
        if self.rank == Meteor.MeteorRank.Big:

            # adds points to score
            self.score.add_to_score(10)

            dir1, dir2, dir3 = self.direction.copy(), self.direction.copy(), self.direction.copy()
            dir2.x = dir2.x + (dir2.x / 10 * 4)
            dir2.y = dir2.y - (dir2.y / 10 * 4)
            dir3.x = dir3.x - (dir3.x / 10 * 4)
            dir3.y = dir3.y + (dir3.y / 10 * 4)
            # print(f"dir1: {dir1} \ndir2: {dir2.normalize()}\ndir3: {dir3.normalize()}\n")
            Meteor(self.scene, Meteor.MeteorRank.Mid, self.transform.world_position_read_only + dir1 * 10, dir1)
            Meteor(self.scene, Meteor.MeteorRank.Mid, self.transform.world_position_read_only + dir2 * 10,
                   dir2.normalize())
            Meteor(self.scene, Meteor.MeteorRank.Mid, self.transform.world_position_read_only + dir3 * 10,
                   dir3.normalize())

        elif self.rank == Meteor.MeteorRank.Mid:

            # adds points to score
            self.score.add_to_score(20)

            dir1, dir2, dir3, dir4, dir5 = self.direction.copy(), self.direction.copy(), self.direction.copy(), \
                                           self.direction.copy(), self.direction.copy()
            dir2.x = dir2.x + (dir2.x / 10 * 4)
            dir2.y = dir2.y - (dir2.y / 10 * 4)
            dir3.x = dir3.x - (dir3.x / 10 * 4)
            dir3.y = dir3.y + (dir3.y / 10 * 4)
            dir4.x = dir4.x + (dir4.x / 10 * 8)
            dir4.y = dir4.y - (dir4.y / 10 * 8)
            dir5.x = dir5.x - (dir5.x / 10 * 8)
            dir5.y = dir5.y + (dir5.y / 10 * 8)
            # print(f"dir1: {dir1} \ndir2: {dir2.normalize()}\ndir3: {dir3.normalize()}\ndir4: {dir4.normalize()}\ndir5: {dir5.normalize()}\n")
            Meteor(self.scene, Meteor.MeteorRank.Small, self.transform.world_position_read_only, dir1)
            Meteor(self.scene, Meteor.MeteorRank.Small, self.transform.world_position_read_only, dir2.normalize())
            Meteor(self.scene, Meteor.MeteorRank.Small, self.transform.world_position_read_only, dir3.normalize())
            Meteor(self.scene, Meteor.MeteorRank.Small, self.transform.world_position_read_only, dir4.normalize())
            Meteor(self.scene, Meteor.MeteorRank.Small, self.transform.world_position_read_only, dir5.normalize())

        elif self.rank == Meteor.MeteorRank.Small:
            # adds points to score
            self.score.add_to_score(30)

    def move_to_direction(self):
        pos_increment = pygame.Vector2(self.direction * self.move_speed * GameTime.DeltaTime)
        self.transform.translate_world_position(pos_increment)

    def _set_to_garbage_collection(self):
        self.scene.remove_game_object(self)

