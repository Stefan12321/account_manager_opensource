from typing import Union, Dict, TypedDict

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QButtonGroup
from qfluentwidgets import ExpandSettingCard, FluentIconBase, RadioButton


class OptionsSettingCard(ExpandSettingCard):
    """ setting card with a group of options """

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title,
                 properties_dict: Dict[str, Dict[str, dict[str, bool] | str]], content=None, parent=None):
        """
        Parameters
        ----------
        configItem: OptionsConfigItem
            options config item

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of setting card

        content: str
            the content of setting card

        properties_dict: Dict[str, bool]
            the dict of properties for radio buttons

        parent: QWidget
            parent window
        """
        super().__init__(icon, title, content, parent)
        self.properties_dict = properties_dict
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        # create buttons
        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)
        for text in properties_dict["values"].keys():
            button = RadioButton(text, self.view)
            self.buttonGroup.addButton(button)
            self.viewLayout.addWidget(button)
            if properties_dict["values"][text]:
                self.setValue(text)

        self._adjustViewSize()
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: RadioButton):
        """ button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        for text in self.properties_dict["values"].keys():
            if text == button.text():
                self.properties_dict["values"][text] = True
            else:
                self.properties_dict["values"][text] = False

    def setValue(self, value):
        """ select button according to the value """

        for button in self.buttonGroup.buttons():
            is_checked = button.text() == value
            button.setChecked(is_checked)

            if is_checked:
                self.choiceLabel.setText(button.text())
                self.choiceLabel.adjustSize()
