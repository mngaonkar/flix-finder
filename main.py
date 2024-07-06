from loguru import logger
from frontend.gui import GUI

def main():
    logger.info("Starting GUI...")
    gui = GUI()
    gui.run()

if __name__ == '__main__':
    main()