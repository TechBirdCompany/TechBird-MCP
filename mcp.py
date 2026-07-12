from nicegui import ui

from gui.main_page import build_main_page

@ui.page('/')
async def main():

    build_main_page()


ui.run(
    title='TechBird MCP',
    reload=False
)