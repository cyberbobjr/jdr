from typing import List, Dict
from uuid import UUID
from back.utils.logger import log_debug

# Logique métier unitaire (SRP)

class InventoryService:
    """
    Service pour gérer l'inventaire des personnages.
    """

    def __init__(self):
        self.inventories = {}

    def add_item(self, player_id: UUID, item_id: str, qty: int = 1) -> Dict:
        """
        Ajoute un objet à l'inventaire d'un joueur.

        Parameters:
        - player_id (UUID): L'identifiant du joueur.
        - item_id (str): L'identifiant de l'objet.
        - qty (int): La quantité à ajouter (par défaut 1).

        Returns:
        - dict: Résumé de l'inventaire mis à jour.
        """
        log_debug("Ajout d'un objet à l'inventaire", action="add_item", player_id=str(player_id), item_id=item_id, qty=qty)
        if player_id not in self.inventories:
            self.inventories[player_id] = {"inventory": {}, "equipped": []}
        inventory = self.inventories[player_id]["inventory"]
        inventory[item_id] = inventory.get(item_id, 0) + qty
        return self.inventories[player_id]

    def remove_item(self, player_id: UUID, item_id: str, qty: int = 1) -> Dict:
        """
        Retire un objet de l'inventaire d'un joueur.

        Parameters:
        - player_id (UUID): L'identifiant du joueur.
        - item_id (str): L'identifiant de l'objet.
        - qty (int): La quantité à retirer (par défaut 1).

        Returns:
        - dict: Résumé de l'inventaire mis à jour.
        """
        log_debug("Retrait d'un objet de l'inventaire", action="remove_item", player_id=str(player_id), item_id=item_id, qty=qty)
        if player_id in self.inventories and item_id in self.inventories[player_id]["inventory"]:
            inventory = self.inventories[player_id]["inventory"]
            inventory[item_id] -= qty
            if inventory[item_id] <= 0:
                del inventory[item_id]
        return self.inventories.get(player_id, {"inventory": {}, "equipped": []})

    def equip_item(self, player_id: UUID, item_id: str) -> Dict:
        """
        Équipe un objet pour un joueur.

        Parameters:
        - player_id (UUID): L'identifiant du joueur.
        - item_id (str): L'identifiant de l'objet.

        Returns:
        - dict: Résumé de l'inventaire mis à jour avec l'objet équipé.
        """
        if player_id in self.inventories and item_id in self.inventories[player_id]["inventory"]:
            self.inventories[player_id]["equipped"].append(item_id)
        return self.inventories.get(player_id, {"inventory": {}, "equipped": []})

    def unequip_item(self, player_id: UUID, item_id: str) -> Dict:
        """
        Déséquipe un objet pour un joueur.

        Parameters:
        - player_id (UUID): L'identifiant du joueur.
        - item_id (str): L'identifiant de l'objet.

        Returns:
        - dict: Résumé de l'inventaire mis à jour avec l'objet déséquipé.
        """
        if player_id in self.inventories and item_id in self.inventories[player_id]["equipped"]:
            self.inventories[player_id]["equipped"].remove(item_id)
        return self.inventories.get(player_id, {"inventory": {}, "equipped": []})
