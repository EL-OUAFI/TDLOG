from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
engine = create_engine('sqlite:////tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
from  sqlalchemy import create_engine,Column,Integer,String,ForeignKey,select
from model.cruiser import Cruiser
from model.destroyer import Destroyer
from model.submarine import Submarine
from model.frigate import Frigate
from model.surface_missile_launcher import SurfaceMissileLauncher
from model.battlefield import Battlefield
from model.vessel import Vessel 
from model.weapon import Weapon
from model.air_missile_launcher import AirMissileLauncher
from model.game import Game
from model.player import Player





class GameEntity(Base):
     __tablename__ = 'game'
id = Column(Integer, primary_key=True)
players = relationship("PlayerEntity", back_populates="game",
 ascade="all, delete-orphan")

class PlayerEntity(Base):
 __tablename__ = 'player'
 id = Column(Integer, primary_key=True)
 name = Column(String, nullable=False)
 game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
 game = relationship("GameEntity", back_populates="players")
 battle_field = relationship("BattlefieldEntity",
 back_populates="player",
 uselist=False, cascade="all, delete-orphan")
 
 
class GameDao:
    
    def map_to_vessels(vessel_entities: list[VesselEntity]):
        vessels:list[vessel]=[]
        for vessel_entity in vessel_entities:
            weapon=map_to_weapon(vessel_entitty,weapon)
            vessel=map_to_vessel(vessel_entitty,weapon)
            vessels.append(vessel)
        return vessels
    def map_to_vessel(vessel_entity,weapon) -> Optional[Vessel]:
        vessel=None
        match vessel_entity.type:
            case VesselType.CRUISER:
                vessel =Cruiser(vessel_entity.coord_x,vessel_entity.coord_y,vessel_entity.coord_z)
                vessel.bits_to_be_destroyer=vessel_entity.hits_to_be_destroyed
                vessel.id=vessel_entity.id
                vessel.weapon=weapon
                return vessel
            case VesselType.DESTROYER:
                vessel=Destroyer(vessel_entity.coord_x,vessel_entity.coord_y,vessel_entity.coord_z)
                vessel.bits_to_be_destroyer=vessel_entity.hits_to_be_destroyed
                vessel.id=vessel_entity.id
                vessel.weapon=weapon
                return vessel
            case VesselType.FRIGATE:
                vessel=Frigate(vessel_entity.coord_x,vessel_entity.coord_y,vessel_entity.coord_z)
                vessel.bits_to_be_destroyer=vessel_entity.hits_to_be_destroyed
                vessel.id=vessel_entity.id
                vessel.weapon=weapon
                return vessel
            case VesselType.SUBMARINE:
                vessel=Submarine(vessel_entity.coord_x,vessel_entity.coord_y,vessel_entity.coord_z)
                vessel.bits_to_be_destroyer=vessel_entity.hits_to_be_destroyed
                vessel.id=vessel_entity.id
                vessel.weapon=weapon
                return vessel
        return vessel
    def map_to_weapon(weapon_entity: WeaponEntity)-> Optional[Weapon]:
        Weapon=None
        match weapon_entity.type:
            case WeaponTypes.SURFACEMISSILELANCHER:
                weapon=SurfaceMissileLauncher()
                return weapon
            case WeaponTypes.SURFACEMISSILELANCHER:
                weapon=AirMissileLauncher()
                return Weapon
                
        return weapon
            
        
    
            
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()
    def create_game(self, game: Game) -> int:
        game_entity = map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id
    def find_game(self, game_id: int) -> Game:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return map_to_game(game_entity)
    
    def map_to_game(game_entity: GameEntity) -> Optional [Game]:
        if game_entity is None:
            return None
        game=Game()
        game.id=game_entity.id
        for player_entity in game_entity.players:
            battle_field=Battlefield(player_entity.battle_field.min_x,
                                        player_entity.battle_field.max_x,
                                        player_entity.battle_field.min_y,
                                        player_entity.battle_field.max_y,
                                        player_entity.battle_field.min_z,
                                        player_entity.battle_field.max_z,
                                        player_entity.battle_field.maw_power)
            battle_field.id=player_entity.battle_field.id
            battle_field.vessels=map_tovessels(player_entity.battle_field.vessels)
            player=Player(player_entity.name, battle_field)
            player.id=player_entity.id
            game.add_player(player)
            return game
    
    def map_to_game_entity(game:Game) -> GameEntity:
        game_entity=GameEntity()
        if game.get_id() is not None:
            game_entity.id=game.get_id()
        for player in game.get_players():
            player_entity=PlayerEntity()  
            player_entity.id=player.id
            player_entity.name=player.get_name() 
            battlefield_entity=map_to_battlefield_entity(player.get_battlefield())
            vessel_entities= \
                map_to_vessel_entities(player.get_battlefield().id,
                                        player.get_battlefield().vessels)
            battlefield_entity.vessels=vessel_entities
            player_entity.battle_field=battlefield_entity
            game-entity.players.append(player_entity)
        return game_entity