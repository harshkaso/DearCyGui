"""
This type stub file was generated by cyright.
"""

import dearcygui as dcg
import numpy as np

class TiledImage(dcg.drawingItem):
    """
    This item enables to easily display a possibly huge
    image by only loading the image times that are currently
    visible.

    The texture management is handled implicitly.
    """
    def get_tile_data(self, uuid: int) -> dict:
        """
        Get tile information
        """
        ...
    
    def get_tile_uuids(self) -> list[int]:
        """
        Get the list of uuids of the tiles.
        """
        ...
    
    def get_oldest_tile(self) -> int:
        """
        Get the uuid of the oldest tile (the one
        with smallest last_frame_count).
        """
        ...
    
    def add_tile(self, content, coord, opposite_coord=..., visible=...) -> None:
        """
        Add a tile to the list of tiles.
        Inputs:
            content: numpy array, the content of the tile
            coord: the top-left coordinate of the tile
            opposite_coord (optional): if not given,
                defaults to coord + content.shape.
                Else corresponds to the opposite coordinate
                of the tile.
            visible (optional): whether the tile should start visible or not.
        Outputs:
            Unique uuid of the tile.
        """
        ...
    
    def remove_tile(self, uuid) -> None:
        """
        Remove a tile from the list of tiles.
        Inputs:
            uuid: the unique identifier of the tile.
        """
        ...
    
    def set_tile_visibility(self, uuid, visible) -> None:
        """
        Set the visibility status of a tile.
        Inputs:
            uuid: the unique identifier of the tile.
            visible: Whether the tile should be visible or not.
        By default tiles start visible.
        """
        ...
    
    def update_tile(self, uuid, content: np.ndarray) -> None:
        """
        Update the content of a tile.
        Inputs:
            uuid: the unique identifier of the tile.
            content: the new content of the tile.
        """
        ...
    


