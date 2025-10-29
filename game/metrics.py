import os
import csv


class Metrics:

    @staticmethod
    def generate_report(
        algorithm, opponent: str, winner: str, points: int, total_points: int
    ):
        """Create the .csv file with the performance metrics."""

        # player statistics
        running_time = algorithm.ejecution_time
        max_ram_usage = algorithm.max_ram_usage
        search_depth = algorithm.depth_explored
        turns = algorithm.turns_played
        nodes_expanded = algorithm.nodes_expanded

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        csv_filename = os.path.join(output_dir, f"{algorithm.name}.csv")
        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, "a", newline="") as f:
            writer = csv.writer(f)
            headers = [
                "opponent",
                "winner",
                "points",
                "Total_points",
                "turns",
                "total_nodes_expanded",
                "total_search_depth",
                "total_running_time",
                "total_max_ram_usage",
            ]
            if not file_exists:
                writer.writerow(headers)

            row_data = [
                opponent,
                winner,
                points,
                total_points,
                turns,
                f"{nodes_expanded/turns:.2f}",
                f"{search_depth/turns:.2f}",
                f"{running_time/turns:.2f}",
                f"{max_ram_usage/turns:.2f}",
            ]
            writer.writerow(row_data)

    @staticmethod
    def generate_vs_report(
        player1: str,
        player2: str,
        winner: str,
        points: int,
        total_points: int,
        depth: int,
    ):
        """Create the .csv file with the performance metrics."""

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        csv_filename = os.path.join(output_dir, f"genetic_vs.csv")
        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, "a", newline="") as f:
            writer = csv.writer(f)
            headers = [
                "player 1",
                "player 2",
                "winner",
                "winner points",
                "Total_points",
                "depth",
            ]
            if not file_exists:
                writer.writerow(headers)

            row_data = [player1, player2, winner, points, total_points, depth]
            writer.writerow(row_data)
