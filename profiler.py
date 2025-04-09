import cProfile
from src.handler import handler


def main():
    handler()


cProfile.run("main()", "output.prof")
