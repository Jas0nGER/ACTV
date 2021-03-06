import ac
import acsys
import math
import functools
from .util.classes import Label, Value, Colors, Font
from .configuration import Configuration


class Driver:
    def __init__(self, app, identifier, name, pos, is_lap_label=False, is_results=False):
        self.identifier = identifier
        self.rowHeight = Configuration.ui_row_height
        self.race = False
        self.race_start_position = -1
        self.cur_theme = Value(-1)
        self.font = Value(0)
        self.theme = Value(-1)
        self.border_direction = Value(-1)
        self.row_height = Value(-1)
        self.hasStartedRace = False
        self.inPitFromPitLane = False
        self.isInPitLane = Value(False)
        self.isInPitLaneOld = False
        self.isInPitBox = Value(False)
        str_offset = " "
        self.final_y = 0
        self.isDisplayed = False
        self.firstDraw = False
        self.isAlive = Value(False)
        self.is_results = is_results
        self.movingUp = False
        self.isCurrentVehicule = Value(False)
        self.isLapLabel = is_lap_label
        self.qual_mode = Value(0)
        self.race_gaps = []
        self.finished = Value(False)
        self.bestLap = 0
        self.compact_mode = False
        self.bestLapServer = 0
        self.lapCount = 0
        self.fullName = Value(name)
        self.shortName = name
        self.time = Value()
        self.gap = Value()
        self.raceProgress = 0
        self.race_current_sector = Value(0)
        self.race_standings_sector = Value(0)
        self.push_2_pass_status = Value(0)
        self.push_2_pass_left = Value(0)
        self.isInPit = Value(False)
        self.completedLaps = Value()
        self.completedLapsChanged = False
        self.last_lap_visible_end = 0
        self.time_highlight_end = 0
        self.position_highlight_end = 0
        self.highlight = Value()
        self.pit_highlight_end = 0
        self.pit_highlight = Value()
        self.position = Value()
        self.position_offset = Value()
        self.carName = ac.getCarName(self.identifier)
        self.num_pos = 0
        self.showingFullNames = False
        fontSize = 28
        if self.isLapLabel:
            self.lbl_name = Label(app, str_offset + name) \
                .set(w=self.rowHeight * 6, h=self.rowHeight,
                     x=0, y=0,
                     font_size=fontSize,
                     align="left",
                     opacity=0)
        elif self.is_results:
            self.lbl_name = Label(app, str_offset + self.format_name_tlc(name)) \
                .set(w=self.rowHeight * 5, h=self.rowHeight,
                     x=self.rowHeight, y=0,
                     font_size=fontSize,
                     align="left",
                     opacity=0)
            self.lbl_position = Label(app, str(pos + 1)) \
                .set(w=self.rowHeight, h=self.rowHeight,
                     x=0, y=0,
                     font_size=fontSize,
                     align="center",
                     opacity=0)
            self.lbl_pit = Label(app, "P") \
                .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=fontSize - 3,
                     align="center",
                     opacity=0)
            self.lbl_pit.setAnimationSpeed("rgb", 0.08)
            self.lbl_position.setAnimationMode("y", "spring")
            self.lbl_pit.setAnimationMode("y", "spring")
        else:
            self.lbl_name = Label(app, str_offset + self.format_name_tlc(name)) \
                .set(w=self.rowHeight * 5, h=self.rowHeight,
                     x=self.rowHeight, y=0,
                     font_size=fontSize,
                     align="left",
                     opacity=0)
            self.lbl_position = Label(app, str(pos + 1)) \
                .set(w=self.rowHeight, h=self.rowHeight,
                     x=0, y=0,
                     font_size=fontSize,
                     align="center",
                     opacity=0)
            self.lbl_pit = Label(app, "P") \
                .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=fontSize - 3,
                     align="center",
                     opacity=0)
            self.lbl_p2p = Label(app, "0") \
                .set(w=self.rowHeight * 0.55, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=fontSize - 3,
                     align="center",
                     opacity=0)
            self.lbl_p2p.setAnimationSpeed("rgb", 0.08)
            self.lbl_pit.setAnimationSpeed("rgb", 0.08)
            self.lbl_position.setAnimationMode("y", "spring")
            self.lbl_p2p.setAnimationMode("y", "spring")
            self.lbl_pit.setAnimationMode("y", "spring")
        self.lbl_time = Label(app, "+0.000") \
            .set(w=self.rowHeight * 4.7, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 font_size=fontSize,
                 align="right",
                 opacity=0)
        self.lbl_border = Label(app, "") \
            .set(w=self.rowHeight * 2.8, h=2,
                 x=0, y=self.rowHeight - 2,
                 background=Colors.red(bg=True),
                 opacity=Colors.border_opacity())
        self.set_name()
        self.lbl_time.setAnimationSpeed("rgb", 0.08)
        self.lbl_name.setAnimationSpeed("w", 2)
        self.lbl_name.setAnimationMode("y", "spring")
        self.lbl_time.setAnimationMode("y", "spring")
        self.lbl_border.setAnimationMode("y", "spring")
        self.redraw_size()

        if not self.isLapLabel:
            self.partial_func = functools.partial(self.on_click_func, driver=self.identifier)
            ac.addOnClickedListener(self.lbl_position.label, self.partial_func)
            ac.addOnClickedListener(self.lbl_name.label, self.partial_func)

    @classmethod
    def on_click_func(*args, driver=0):
        ac.focusCar(driver)

    def redraw_size(self):
        # Config
        self.row_height.setValue(Configuration.ui_row_height)
        self.border_direction.setValue(Colors.border_direction)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.font.setValue(Font.current)
        self.rowHeight = self.row_height.value
        font_size = Font.get_font_size(self.rowHeight + Font.get_font_offset())
        if Colors.border_direction == 1:
            border_offset = 8
        else:
            border_offset = 4
        # Colors
        if self.theme.hasChanged():
            if not self.isLapLabel:
                self.set_border()
                if self.pit_highlight.value:
                    self.lbl_pit.set(color=Colors.tower_pit_highlight_txt(), animated=True, init=True)
                else:
                    self.lbl_pit.set(color=Colors.tower_pit_txt(), animated=True, init=True)
            if self.race:
                battles = True
            else:
                battles = False
            if self.position.value % 2 == 1:
                if not self.isLapLabel:
                    if self.position.value == 1 and Colors.tower_first_position_different():
                        self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                          color=Colors.tower_driver_odd_txt(),
                                          animated=True, init=True)
                        self.lbl_time.set(color=Colors.tower_time_odd_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_first_bg(),
                                              color=Colors.tower_position_first_txt(),
                                              animated=True, init=True)
                    elif battles and self.isCurrentVehicule.value:
                        self.lbl_name.set(background=Colors.tower_driver_highlight_odd_bg(),
                                          color=Colors.tower_driver_highlight_odd_txt(),
                                          animated=True, init=True)
                        self.lbl_time.set(color=Colors.tower_time_highlight_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(),
                                              color=Colors.tower_position_highlight_odd_txt(),
                                              animated=True, init=True)
                    else:
                        self.lbl_time.set(color=Colors.tower_time_odd_txt(),
                                          animated=True, init=True)
                        if self.isAlive.value:
                            self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                              color=Colors.tower_driver_odd_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_odd_bg(),
                                                  color=Colors.tower_position_odd_txt(),
                                                  animated=True, init=True)
                        else:
                            self.lbl_name.set(background=Colors.tower_driver_retired_bg(),
                                              color=Colors.tower_driver_retired_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_odd_bg(),
                                                  color=Colors.tower_position_retired_txt(),
                                                  animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                      color=Colors.tower_driver_odd_txt(),
                                      animated=True, init=True)
                    self.lbl_time.set(color=Colors.tower_time_odd_txt(),
                                      animated=True, init=True)

            else:
                if not self.isLapLabel:
                    if battles and self.isCurrentVehicule.value:
                        self.lbl_name.set(background=Colors.tower_driver_highlight_even_bg(),
                                          color=Colors.tower_driver_highlight_even_txt(),
                                          animated=True, init=True)
                        self.lbl_time.set(color=Colors.tower_time_highlight_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_highlight_even_bg(),
                                              color=Colors.tower_position_highlight_even_txt(),
                                              animated=True, init=True)
                    else:
                        self.lbl_time.set(color=Colors.tower_time_even_txt(),
                                          animated=True, init=True)
                        if self.isAlive.value:
                            self.lbl_name.set(background=Colors.tower_driver_even_bg(),
                                              color=Colors.tower_driver_even_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_even_bg(),
                                                  color=Colors.tower_position_even_txt(),
                                                  animated=True, init=True)
                        else:
                            self.lbl_name.set(background=Colors.tower_driver_retired_bg(),
                                              color=Colors.tower_driver_retired_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_even_bg(),
                                                  color=Colors.tower_position_retired_txt(),
                                                  animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_even_bg(),
                                      color=Colors.tower_driver_even_txt(),
                                      animated=True, init=True)
                    self.lbl_time.set(color=Colors.tower_time_even_txt(),
                                      animated=True, init=True)
        font_changed = self.font.hasChanged()
        if self.row_height.hasChanged() or font_changed or self.border_direction.hasChanged():
            # Fonts
            if font_changed:
                self.lbl_name.update_font()
                self.lbl_time.update_font()
                if not self.isLapLabel:
                    self.lbl_position.update_font()
                    self.lbl_pit.update_font()
                    self.lbl_p2p.update_font()
            # UI
            #self.position.setValue(-1)
            if self.isLapLabel:
                self.lbl_name.set(w=self.rowHeight * 6.2 + border_offset,
                                  h=self.rowHeight,
                                  x=0,
                                  font_size=font_size)
            else:
                self.lbl_name.set(w=self.get_name_width(),
                                  h=self.rowHeight,
                                  x=self.rowHeight + border_offset,
                                  font_size=font_size)
                self.lbl_position.set(w=self.rowHeight + 4, h=self.rowHeight,
                                      font_size=font_size)
                self.lbl_pit.set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                                 x=self.get_pit_x(),
                                 font_size=font_size - 3, animated=True)
                self.lbl_p2p.set(w=self.rowHeight * 0.55, h=self.rowHeight - 2,
                                 x=self.get_pit_x(),
                                 font_size=font_size - 6, animated=True)
            # Names
            lbl_multi = 1.2
            if Configuration.names >= 2:  # First Last
                self.show_full_name()
                lbl_multi = 4.3
            else:  # TLC
                self.set_name()

            self.lbl_time.set(w=self.rowHeight * 4.7, h=self.rowHeight,
                              x=self.rowHeight*lbl_multi + border_offset,
                              font_size=font_size, animated=True)
            if Colors.border_direction == 1:
                self.lbl_border.set(w=4, h=self.rowHeight,
                                    x=self.rowHeight + 4, y=self.final_y)
            else:
                self.lbl_border.set(w=self.rowHeight * 2.8, h=2,
                                    x=0, y=self.final_y + self.rowHeight - 2)
            if self.isDisplayed:
                self.final_y = self.num_pos * self.rowHeight
                if self.isLapLabel:
                    self.lbl_name.setPos(0, self.final_y, True)
                else:
                    self.lbl_position.setText(str(self.position.value))
                    self.lbl_name.setY(self.final_y, True)
                    self.lbl_position.setY(self.final_y, True)
                    self.lbl_pit.setY(self.final_y + 3, True)
                    self.lbl_p2p.setY(self.final_y + 5, True)

                self.lbl_time.setY(self.final_y, True)
                if Colors.border_direction == 1:
                    self.lbl_border.setY(self.final_y, True)
                else:
                    self.lbl_border.setY(self.final_y + self.rowHeight - 2, True)

    def show(self, needs_tlc=True, race=True, compact=False):
        self.race = race
        self.compact_mode = compact
        #P2P
        if not self.isLapLabel:
            if not self.isInPit.value and self.push_2_pass_status.value > 0 and not self.finished.value:
                self.lbl_p2p.setX(self.get_pit_x(), self.isDisplayed)
                self.lbl_p2p.show()
            else:
                self.lbl_p2p.hide()
        if self.showingFullNames and needs_tlc:
            self.set_name()
        elif not self.showingFullNames and not needs_tlc:
            self.show_full_name()
        if not self.isDisplayed:
            if not self.isLapLabel:
                self.lbl_name.set(w=self.get_name_width())
            self.isDisplayed = True
        self.lbl_name.show()

        if not self.is_compact_mode():
            self.lbl_time.show()
        else:
            self.lbl_time.hide()

        if (self.isLapLabel and Colors.border_direction == 0) or not self.isLapLabel:
            self.lbl_border.show()
        else:
            self.lbl_border.hide()
        if not self.isLapLabel:
            self.lbl_position.show()
            if not self.isAlive.value and not self.finished.value:
                self.lbl_name.setColor(Colors.tower_driver_retired_txt(), animated=True, init=True)
            elif self.isInPit.value or ac.getCarState(self.identifier, acsys.CS.SpeedKMH) > 30 or self.finished.value:
                if self.race and self.isCurrentVehicule.value:
                    if self.position.value % 2 == 1:
                        self.lbl_name.setColor(Colors.tower_driver_highlight_odd_txt(), animated=True, init=True)
                    else:
                        self.lbl_name.setColor(Colors.tower_driver_highlight_even_txt(), animated=True, init=True)
                elif self.position.value % 2 == 1:
                    self.lbl_name.setColor(Colors.tower_driver_odd_txt(), animated=True, init=True)
                else:
                    self.lbl_name.setColor(Colors.tower_driver_even_txt(), animated=True, init=True)
            else:
                self.lbl_name.setColor(Colors.tower_driver_stopped_txt(), animated=True, init=True)

    def update_pit(self, session_time):
        if not self.isLapLabel and self.isInPit.hasChanged():
            if self.isInPit.value:
                self.pit_highlight_end = session_time - 5000
                self.lbl_pit.setX(self.get_pit_x(), True)
                self.lbl_pit.show()
                self.lbl_name.setSize(self.get_name_width(), self.rowHeight, True)
            else:
                self.lbl_pit.hide()
                self.lbl_name.setSize(self.get_name_width(), self.rowHeight, True)
        if self.isInPit.value and (self.lbl_name.f_params["w"].value < self.rowHeight * 5.6 or self.lbl_pit.f_params["a"].value < 1):
            self.lbl_pit.setX(self.get_pit_x(), True)
            self.lbl_pit.show()
            self.lbl_name.setSize(self.get_name_width(), self.rowHeight, True)
        elif not self.isInPit.value and (self.lbl_name.f_params["w"].value > self.rowHeight * 5 or self.lbl_pit.f_params["a"].value == 1):
            self.lbl_pit.hide()
            self.lbl_name.setSize(self.get_name_width(), self.rowHeight, True)
        if session_time == -1:
            self.pit_highlight_end = 0
        self.pit_highlight.setValue(self.pit_highlight_end != 0 and self.pit_highlight_end < session_time)
        if self.pit_highlight.hasChanged():
            if self.pit_highlight.value:
                self.lbl_pit.setColor(Colors.tower_pit_highlight_txt(), init=True)
            else:
                self.lbl_pit.setColor(Colors.tower_pit_txt(), animated=True, init=True)

    def hide(self, reset=False):
        if not self.isLapLabel:
            self.lbl_position.hide()
            self.lbl_pit.hide()
            self.lbl_p2p.hide()
            if self.isInPit.value:
                self.lbl_name.setSize(self.get_name_width(), self.rowHeight)
            else:
                self.lbl_name.setSize(self.get_name_width(), self.rowHeight)
        self.lbl_time.hide()
        self.lbl_border.hide()
        self.lbl_name.hide()
        self.isDisplayed = False
        if reset:
            self.finished.setValue(False)
            self.isInPit.setValue(False)
            self.firstDraw = False
            self.set_name()
            self.race_current_sector.setValue(0)
            self.race_standings_sector.setValue(0)
            self.race_gaps = []
            self.completedLaps.setValue(0)
            self.completedLapsChanged = False
            self.last_lap_visible_end = 0
            self.time_highlight_end = 0
            self.bestLap = 0
            self.bestLapServer = 0
            self.position_highlight_end = 0
            self.inPitFromPitLane = False
            self.hasStartedRace = False
            self.isInPitBox.setValue(False)
            self.push_2_pass_status.setValue(0)
            self.push_2_pass_left.setValue(0)

    def get_best_lap(self, lap=False):
        if lap:
            self.bestLap = lap
        if self.bestLapServer > 0 and self.bestLap > 0:
            if self.bestLapServer > self.bestLap:
                return self.bestLap
            else:
                return self.bestLapServer
        if self.bestLapServer > 0:
            return self.bestLapServer
        if self.bestLap > 0:
            return self.bestLap
        return 0

    def set_name(self):
        self.showingFullNames = False
        offset = " "
        if self.isLapLabel:
            self.lbl_name.setText(offset + self.fullName.value)
        else:
            if Configuration.names == 1:
                self.lbl_name.setText(offset + self.format_name_tlc2(self.fullName.value))
            else:
                self.lbl_name.setText(offset + self.format_name_tlc(self.fullName.value))
            self.set_border()

    def set_border(self):
        colors_by_class = bool(Configuration.carColorsBy == 1)
        self.lbl_border.set(background=Colors.colorFromCar(self.carName, colors_by_class, Colors.tower_border_default_bg()),
                            init=True)

    def show_full_name(self):
        offset = " "
        self.showingFullNames = True
        if self.isLapLabel:
            self.lbl_name.setText(offset + self.fullName.value)
        else:
            if Configuration.names == 4:
                self.lbl_name.setText(offset + self.format_first_name(self.fullName.value))
            elif Configuration.names == 3:
                self.lbl_name.setText(offset + self.format_last_name2(self.fullName.value))
            else:
                self.lbl_name.setText(offset + self.format_last_name(self.fullName.value))

    def set_time(self, time, leader, session_time, mode):
        if self.highlight.value:
            if mode == 0:
                mode = 1
        self.qual_mode.setValue(mode)
        self.time.setValue(time)
        self.gap.setValue(time - leader)
        time_changed = self.time.hasChanged()
        if time_changed or self.gap.hasChanged() or self.qual_mode.hasChanged():
            if time_changed:
                self.time_highlight_end = session_time - 5000
            if self.position.value == 1 or mode == 1:
                self.lbl_time.change_font_if_needed().setText(self.format_time(self.time.value))
            else:
                self.lbl_time.change_font_if_needed().setText("+" + self.format_time(self.gap.value))

    def set_time_stint(self, time, valid):
        self.time.setValue(time)
        self.gap.setValue(time)
        if self.time.hasChanged() or self.gap.hasChanged():
            self.lbl_time.change_font_if_needed().setText(self.format_time(self.time.value))
            if valid:
                if self.position.value % 2 == 1:
                    self.lbl_time.setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
                else:
                    self.lbl_time.setColor(Colors.tower_time_even_txt(), animated=True, init=True)
            else:
                self.lbl_time.setColor(Colors.tower_stint_lap_invalid_txt(), animated=True, init=True)

    def set_time_race(self, time, leader, session_time):
        if self.position.value == 1:
            self.lbl_time.change_font_if_needed().setText("Lap " + str(time)).setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
        elif self.position.value % 2 == 1:
            self.lbl_time.change_font_if_needed().setText("+" + self.format_time(leader - session_time)).setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
        else:
            self.lbl_time.change_font_if_needed().setText("+" + self.format_time(leader - session_time)).setColor(Colors.tower_time_even_txt(), animated=True, init=True)

    def set_time_race_battle(self, time, identifier, lap=False, intervals=False):
        if self.isCurrentVehicule.value:
            normal_color = Colors.tower_time_highlight_txt()
        elif self.position.value % 2 == 1:
            normal_color = Colors.tower_time_odd_txt()
        else:
            normal_color = Colors.tower_time_even_txt()
        if time == "PIT":
            self.lbl_time.change_font_if_needed().setText("PIT").setColor(Colors.tower_time_pit_txt(), animated=True, init=True)
        elif time == "DNF":
            self.lbl_time.change_font_if_needed().setText("DNF").setColor(Colors.tower_time_retired_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("UP") >= 0:
            self.lbl_time.change_font_if_needed(1).setText(time.replace("UP", u"\u25B2")).setColor(Colors.tower_time_place_gain_txt(), animated=True, init=True)
            #self.lbl_time.change_font_if_needed(1).setText(u"\u25B2").setColor(Colors.tower_time_place_gain_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("DOWN") >= 0:
            self.lbl_time.change_font_if_needed(1).setText(time.replace("DOWN", u"\u25BC")).setColor(Colors.tower_time_place_lost_txt(), animated=True, init=True)
            #self.lbl_time.change_font_if_needed(1).setText(u"\u25BC").setColor(Colors.tower_time_place_lost_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("NEUTRAL") >= 0:
            self.lbl_time.change_font_if_needed(1).setText(time.replace("NEUTRAL", u"\u25C0")).setColor(normal_color, animated=True, init=True)
        elif self.identifier == identifier or time == 600000:
            self.lbl_time.change_font_if_needed().setText("").setColor(normal_color, animated=True, init=True)
        elif lap:
            str_time = "+" + str(math.floor(abs(time)))
            if abs(time) >= 2:
                str_time += " Laps"
            else:
                str_time += " Lap"
            self.lbl_time.change_font_if_needed().setText(str_time).setColor(normal_color, animated=True, init=True)
        elif identifier == -1:
            if time <= ac.getCarState(self.identifier, acsys.CS.BestLap):
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.tower_time_best_lap_txt(), animated=True, init=True)
            else:
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
        else:
            if intervals:
                self.lbl_time.change_font_if_needed().setText("+" + self.format_time(time)).setColor(normal_color, animated=True, init=True)
            else:
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(normal_color, animated=True, init=True)

    def optimise(self):
        if len(self.race_gaps) > 132:
            del self.race_gaps[0:len(self.race_gaps) - 132]

    def set_position(self, position, offset, battles):
        if not self.isLapLabel:
            self.isInPitLane.setValue(bool(ac.isCarInPitline(self.identifier)))
            self.isInPitBox.setValue(bool(ac.isCarInPit(self.identifier)))
            pit_value = self.isInPitLane.value or self.isInPitBox.value
            self.isInPit.setValue(pit_value)
            if self.race:
                if self.isInPitBox.hasChanged():
                    if self.isInPitBox.value:
                        self.inPitFromPitLane = self.isInPitLaneOld
                    else:
                        self.inPitFromPitLane = False
                self.isInPitLaneOld = self.isInPitLane.value

        self.position.setValue(position)
        self.position_offset.setValue(offset)
        position_changed = self.position.hasChanged()
        if position_changed or self.position_offset.hasChanged() or self.isCurrentVehicule.hasChanged() or self.isAlive.hasChanged():
            if position_changed:
                if self.position.value < self.position.old:
                    self.movingUp = True
                else:
                    self.movingUp = False
                if self.position.old > 0:
                    self.position_highlight_end = True
            # move labels
            self.num_pos = position - 1 - offset
            self.final_y = self.num_pos * self.rowHeight
            # avoid long slide on first draw
            if not self.firstDraw:
                if self.isLapLabel:
                    self.lbl_name.setY(self.final_y)
                else:
                    self.lbl_name.setY(self.final_y)
                    self.lbl_position.setY(self.final_y)
                    self.lbl_pit.setY(self.final_y + 3)
                    self.lbl_p2p.setY(self.final_y + 5)
                self.lbl_time.setY(self.final_y)
                if Colors.border_direction == 1:
                    self.lbl_border.setY(self.final_y)
                else:
                    self.lbl_border.setY(self.final_y + self.rowHeight - 2)
                self.firstDraw = True

            if self.isLapLabel:
                self.lbl_name.setPos(0, self.final_y, True)
            else:
                self.lbl_position.setText(str(self.position.value))
                self.lbl_name.setY(self.final_y, True)
                self.lbl_position.setY(self.final_y, True)
                self.lbl_pit.setY(self.final_y + 3, True)
                self.lbl_p2p.setY(self.final_y + 5, True)

            self.lbl_time.setY(self.final_y, True)
            if Colors.border_direction == 1:
                self.lbl_border.setY(self.final_y, True)
            else:
                self.lbl_border.setY(self.final_y + self.rowHeight - 2, True)
            # ------------------- Colors -----------------
            if position % 2 == 1:
                if not self.isLapLabel:
                    if position == 1 and Colors.tower_first_position_different():
                        self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                          color=Colors.tower_driver_odd_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_first_bg(),
                                              color=Colors.tower_position_first_txt(),
                                              animated=True, init=True)
                    elif battles and self.isCurrentVehicule.value:
                        self.lbl_name.set(background=Colors.tower_driver_highlight_odd_bg(),
                                          color=Colors.tower_driver_highlight_odd_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(),
                                              color=Colors.tower_position_highlight_odd_txt(),
                                              animated=True, init=True)
                    else:
                        if self.isAlive.value:
                            self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                              color=Colors.tower_driver_odd_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_odd_bg(),
                                                  color=Colors.tower_position_odd_txt(),
                                                  animated=True, init=True)
                        else:
                            self.lbl_name.set(background=Colors.tower_driver_retired_bg(),
                                              color=Colors.tower_driver_retired_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_odd_bg(),
                                                  color=Colors.tower_position_retired_txt(),
                                                  animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_odd_bg(),
                                      color=Colors.tower_driver_odd_txt(),
                                      animated=True, init=True)
                    self.lbl_time.set(color=Colors.tower_time_odd_txt(),
                                      animated=True, init=True)
            else:
                if not self.isLapLabel:
                    if battles and self.isCurrentVehicule.value:
                        self.lbl_name.set(background=Colors.tower_driver_highlight_even_bg(),
                                          color=Colors.tower_driver_highlight_even_txt(),
                                          animated=True, init=True)
                        self.lbl_position.set(background=Colors.tower_position_highlight_even_bg(),
                                              color=Colors.tower_position_highlight_even_txt(),
                                              animated=True, init=True)
                    else:
                        if self.isAlive.value:
                            self.lbl_name.set(background=Colors.tower_driver_even_bg(),
                                              color=Colors.tower_driver_even_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_even_bg(),
                                                  color=Colors.tower_position_even_txt(),
                                                  animated=True, init=True)
                        else:
                            self.lbl_name.set(background=Colors.tower_driver_retired_bg(),
                                              color=Colors.tower_driver_retired_txt(),
                                              animated=True, init=True)
                            self.lbl_position.set(background=Colors.tower_position_even_bg(),
                                                  color=Colors.tower_position_retired_txt(),
                                                  animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_even_bg(),
                                      color=Colors.tower_driver_even_txt(),
                                      animated=True, init=True)
                    self.lbl_time.set(color=Colors.tower_time_even_txt(),
                                      animated=True, init=True)

        if not self.isLapLabel:
            self.fullName.setValue(ac.getDriverName(self.identifier))
            if self.fullName.hasChanged():
                # Reset
                self.finished.setValue(False)
                self.set_name()
                self.race_current_sector.setValue(0)
                self.race_standings_sector.setValue(0)
                self.race_gaps = []
                self.completedLaps.setValue(0)
                self.completedLapsChanged = False
                self.last_lap_visible_end = 0
                self.time_highlight_end = 0
                self.bestLap = 0
                self.bestLapServer = 0
                self.position_highlight_end = 0
                self.inPitFromPitLane = False
                self.hasStartedRace = False
                self.isInPitBox.setValue(False)

    def format_name_tlc(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 2:
            return name[:3]
        return name

    def format_name_tlc2(self, name):
        first = ""
        if len(name) > 0:
            first = name[0].upper()
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 2 and len(first) > 0:
            return first + name[:2]
        if len(name) > 2:
            return name[:3]
        return name

    def format_last_name(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 9:
            return name[:10]
        return name

    def format_last_name2(self, name):
        first = ""
        if len(name) > 0:
            first = name[0].upper()
        space = name.find(" ")
        if space > 0:
            name = first + "." + name[space:]
        name = name.strip().upper()
        if len(name) > 9:
            return name[:10]
        return name

    def format_first_name(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[:space]
        name = name.strip().upper()
        if len(name) > 9:
            return name[:10]
        return name

    def format_time(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        d = ms % 1000
        if math.isnan(s) or math.isnan(d) or math.isnan(m) or math.isnan(h):
            return ""
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        elif m > 0:
            return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
        else:
            return "{0}.{1}".format(int(s), str(int(d)).zfill(3))

    def is_compact_mode(self):
        if self.isLapLabel:
            return False
        if not self.race and self.compact_mode and not self.highlight.value:
            return True
        if self.race and self.compact_mode:
            return True
        return False

    def get_name_width(self):
        # Name
        if self.showingFullNames:  # Configuration.names >= 2:
            name_width = 5.2
        else:
            name_width = 2.1
        # Time
        if not self.is_compact_mode():
            name_width += 3.1
        # Pit and P2P
        if self.isInPit.value and not self.finished.value:
            if self.is_compact_mode() or not self.race:
                name_width += 0.6
        elif self.push_2_pass_status.value > 0 and not self.finished.value:
            name_width += 0.6
        return self.rowHeight * name_width

    def get_pit_x(self):
        # Name
        if self.showingFullNames:  # Configuration.names >= 2:
            pit_x = 6.2
        else:
            pit_x = 3.1
        # Time
        if not self.is_compact_mode():
            pit_x += 3.1
        if Colors.border_direction == 1:
            pit_offset = 7
        else:
            pit_offset = 4
        return self.rowHeight * pit_x + pit_offset

    def animate(self, session_time_left):
        if session_time_left == -1:
            self.time_highlight_end = 0
        if not self.isLapLabel:
            # Anything that needs live changes
            if self.isDisplayed:
                self.cur_theme.setValue(Colors.general_theme)
                # Push 2 Pass
                self.push_2_pass_status.setValue(ac.getCarState(self.identifier, acsys.CS.P2PStatus))
                if self.push_2_pass_status.value > 0:  # OFF = 0
                    self.push_2_pass_left.setValue(ac.getCarState(self.identifier, acsys.CS.P2PActivations))
                    if self.push_2_pass_status.hasChanged() or self.cur_theme.hasChanged():
                        if self.push_2_pass_status.value == 1:  # COOLING = 1
                            self.lbl_p2p.setColor(Colors.tower_p2p_cooling(), animated=True, init=True)
                        elif self.push_2_pass_status.value == 2:  # AVAILABLE = 2
                            self.lbl_p2p.setColor(Colors.tower_p2p_txt(), animated=True, init=True)
                        elif self.push_2_pass_status.value == 3:  # ACTIVE = 3
                            self.lbl_p2p.setColor(Colors.tower_p2p_active(), animated=True, init=True)
                    if self.push_2_pass_left.hasChanged():
                        self.lbl_p2p.setText(str(self.push_2_pass_left.value))
                self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < session_time_left)
                if not self.race and self.isDisplayed:
                    if self.highlight.hasChanged():
                        if self.highlight.value:
                            self.lbl_time.setColor(Colors.tower_time_qualification_highlight_txt(), animated=True, init=True)
                            self.lbl_time.show()
                        else:
                            if self.position.value % 2 == 1:
                                self.lbl_time.setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
                            else:
                                self.lbl_time.setColor(Colors.tower_time_even_txt(), animated=True, init=True)

                            if self.is_compact_mode():
                                self.lbl_time.hide()
                            else:
                                self.lbl_time.show()
                    self.lbl_name.set(w=self.get_name_width(), animated=True)
                    self.lbl_pit.setX(self.get_pit_x(), True)
                elif self.race and self.isDisplayed:
                    if self.is_compact_mode() and self.isInPit.value and self.isDisplayed and self.isAlive.value and not self.finished.value:
                        self.lbl_pit.setX(self.get_pit_x(), True)
                        self.lbl_pit.setColor(Colors.tower_pit_txt(), animated=True, init=True)
                        self.lbl_pit.show()
                    else:
                        self.lbl_pit.hide()
                    self.lbl_name.set(w=self.get_name_width(), animated=True)
            # not isLapLabel
            self.lbl_position.animate()
            self.lbl_pit.animate()
            self.lbl_p2p.animate()
        self.lbl_border.animate()
        self.lbl_time.animate()
        self.lbl_name.animate()
