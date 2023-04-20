#!/usr/local/bin/python3

import random


class Player:

    def __init__(self, player_name: str) -> None:
        self.player_name = player_name
        self.record = 0

    def __str__(self) -> str:
        return f"I am {self.player_name}"
    
    def create_player_code_sequence(self, colours: tuple, peg_count: int) -> list[str]:
        player_code_sequence_input = input(f"Enter your sequence of {peg_count} pegs, using ({', '.join(colours)}) colours: ")
        player_code_sequence = [_ for _ in player_code_sequence_input.strip().upper() if _ in colours]
        return player_code_sequence


class Game:
    """
    Класс описывает поведение игры.
    """
    COLOURS = {'R': 'red', 'Y': 'yellow', 'G': 'green', 'B': 'blue'}

    def __init__(self, peg_count: int = 4, try_count: int = 10) -> None:
        self.peg_count = peg_count
        self.try_count = try_count
        self.code_sequence = None
        self.player = None

    def create_code_sequence(self) -> list[str]:
        """Метод создаёт кодовую комбинацию.

        Returns:
            list[str]: 
        """
        code_sequence = []
        for i in range(self.peg_count):
            code_sequence.append(random.choice(tuple(self.COLOURS.keys())))
        return code_sequence

    def create_player(self) -> Player:
        """Метод создаёт игрока и возвращает экземпляр класса Player.

        Returns:
            Player: экземпляр класса Player
        """
        player_name = input("Enter your name: ")
        return Player(player_name)

    def row_analyse_result(self, player_code_sequence: list[str], code_sequence: list[str]) -> tuple[int, int]:
        game_vs_player_sequence = list(zip(code_sequence, player_code_sequence))
        game_displaced_peg_count = {}
        player_displaced_peg_count = {}
        right_pegs_count = 0
        displaced_pegs_count = 0
        for el in game_vs_player_sequence:
            if el[0] == el[1]:
                right_pegs_count += 1
            else:
                game_displaced_peg_count[el[0]] = game_displaced_peg_count.get(el[0], 0) + 1
                player_displaced_peg_count[el[1]] = player_displaced_peg_count.get(el[1], 0) + 1
        for key, value in player_displaced_peg_count.items():
            if key in game_displaced_peg_count:
                displaced_pegs_count += min(value, game_displaced_peg_count[key])
        return right_pegs_count, displaced_pegs_count

    def main(self) -> None:
        """Метод ведёт основную игру: создаётся игрок, создаётся комбинация...
        """
        self.player = self.create_player()
        print(self.player)
        code_sequence = self.create_code_sequence()
        print(f"Game sequence: {self.code_sequence}")
        for i in range(self.try_count):

            player_code_sequence = []
            while len(player_code_sequence) != self.peg_count:
                player_code_sequence = self.player.create_player_code_sequence(self.COLOURS.keys(), self.peg_count)
            right_pegs_count, displaced_pegs_count = self.row_analyse_result(player_code_sequence, code_sequence)
            if right_pegs_count == self.peg_count:
                print("Victory! You are great!")
                print(f"Game combination: {self.code_sequence}")
                print(f"Counts: {i + 1}")
                break
            print(f"Red: {right_pegs_count}, white: {displaced_pegs_count}")


if __name__ == "__main__":
    new_game = Game()
    new_game.main()
    