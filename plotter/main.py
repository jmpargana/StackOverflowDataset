from plotter import Plotter
import os


def main():
    plotter = Plotter(
        os.getenv("MONGO_URI") or "mongodb://mongo_app:27017/",
        os.getenv("MAX_TAGS") or 35,
    )
    plotter.create_graph()


if __name__ == "__main__":
    main()
