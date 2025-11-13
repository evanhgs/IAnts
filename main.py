from gui_progam import MetaProgramConfig

if __name__ == "__main__":
    app = MetaProgramConfig(init_speed_given=10)
    app.settings_menu()
    if app.config:
        app.running = True
        app.run_simulation()
