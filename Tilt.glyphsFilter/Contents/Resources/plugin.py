# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Filter with dialog Plugin: 3D Tilt
#
#	Tilts the layer in 3D (real perspective, so parallel edges converge into a trapezoid)
#	around the center of its bounding box.
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter
#
#	Copyright Rainer Erich Scheichelbauer (@mekkablue)
#	Licensed under the Apache License, Version 2.0, see LICENSE.
#
#
###########################################################################################################

import copy
import objc
from math import radians, sin, cos
from Foundation import NSPoint
from GlyphsApp import Glyphs
from GlyphsApp.plugins import FilterWithDialog
from vanilla import Window, Group, TextBox, EditText

MENU_NAME = {
	"en": "3D Tilt",
	"de": "3D-Kippen",
	"fr": "Inclinaison 3D",
	"it": "Inclinazione 3D",
	"pt": "Inclinação 3D",
	"es": "Inclinación 3D",
	"ko": "3D 기울이기",
	"cs": "3D náklon",
	"ja": "3D傾斜",
	"zh-Hans": "3D倾斜",
	"zh-Hant": "3D傾斜",
}

ACTION_BUTTON_LABEL = {
	"en": "Tilt",
	"de": "Kippen",
	"fr": "Incliner",
	"it": "Inclina",
	"pt": "Inclinar",
	"es": "Inclinar",
	"ko": "기울이기",
	"cs": "Naklonit",
	"ja": "傾ける",
	"zh-Hans": "倾斜",
	"zh-Hant": "傾斜",
}

ANGLE_LABEL = {
	"en": "Angle",
	"de": "Winkel",
	"fr": "Angle",
	"it": "Angolo",
	"pt": "Ângulo",
	"es": "Ángulo",
	"ko": "각도",
	"cs": "Úhel",
	"ja": "角度",
	"zh-Hans": "角度",
	"zh-Hant": "角度",
}

ANGLE_TOOLTIP = {
	"en": "Direction of the tilt in degrees. 0 = north, counterclockwise.",
	"de": "Richtung der Kippung in Grad. 0 = Norden, gegen den Uhrzeigersinn.",
	"fr": "Direction de l’inclinaison en degrés. 0 = nord, sens antihoraire.",
	"it": "Direzione dell’inclinazione in gradi. 0 = nord, in senso antiorario.",
	"pt": "Direção da inclinação em graus. 0 = norte, sentido anti-horário.",
	"es": "Dirección de la inclinación en grados. 0 = norte, sentido antihorario.",
	"ko": "기울임 방향(도). 0 = 북쪽, 반시계 방향.",
	"cs": "Směr náklonu ve stupních. 0 = sever, proti směru hodinových ručiček.",
	"ja": "傾ける方向（度）。0 = 北、反時計回り。",
	"zh-Hans": "倾斜方向（度）。0 = 北，逆时针。",
	"zh-Hant": "傾斜方向（度）。0 = 北，逆時針。",
}

TILT_LABEL = {
	"en": "Tilt",
	"de": "Kippung",
	"fr": "Inclinaison",
	"it": "Inclinazione",
	"pt": "Inclinação",
	"es": "Inclinación",
	"ko": "기울기",
	"cs": "Náklon",
	"ja": "傾き",
	"zh-Hans": "倾斜度",
	"zh-Hant": "傾斜度",
}

TILT_TOOLTIP = {
	"en": "Tilt of the plane in degrees. The side in the angle direction moves away from the viewer.",
	"de": "Kippung der Ebene in Grad. Die Seite in Winkelrichtung wandert vom Betrachter weg.",
	"fr": "Inclinaison du plan en degrés. Le côté situé dans la direction de l’angle s’éloigne de l’observateur.",
	"it": "Inclinazione del piano in gradi. Il lato nella direzione dell’angolo si allontana dall’osservatore.",
	"pt": "Inclinação do plano em graus. O lado na direção do ângulo afasta-se do observador.",
	"es": "Inclinación del plano en grados. El lado en la dirección del ángulo se aleja del observador.",
	"ko": "평면의 기울기(도). 각도 방향의 면이 보는 사람에게서 멀어집니다.",
	"cs": "Náklon roviny ve stupních. Strana ve směru úhlu se vzdaluje od pozorovatele.",
	"ja": "平面の傾き（度）。角度の方向の側が観察者から遠ざかります。",
	"zh-Hans": "平面的倾斜度（度）。角度方向的一侧远离观察者。",
	"zh-Hant": "平面的傾斜度（度）。角度方向的一側遠離觀察者。",
}


def tiltedPosition(position, center, angle, tilt, distance):
	"""
	Returns the NSPoint position after tilting the plane around center.
	angle: direction of the tilt in degrees (0 = north, counterclockwise)
	tilt: tilt of the plane in degrees; the side in the angle direction moves away from the viewer
	distance: distance of the viewer from the plane in units
	"""
	angleRadians = radians(angle)
	directionX = -sin(angleRadians)
	directionY = cos(angleRadians)
	tiltRadians = radians(tilt)

	relativeX = position.x - center.x
	relativeY = position.y - center.y
	along = relativeX * directionX + relativeY * directionY  # coordinate in tilt direction
	across = -relativeX * directionY + relativeY * directionX  # coordinate perpendicular to it
	scale = distance / (distance + along * sin(tiltRadians))  # perspective divide
	newAlong = along * cos(tiltRadians) * scale
	newAcross = across * scale
	return NSPoint(
		center.x + newAlong * directionX - newAcross * directionY,
		center.y + newAlong * directionY + newAcross * directionX,
	)


class Tilt(FilterWithDialog):

	@objc.python_method
	def prefDomain(self, prefName):
		return f"com.mekkablue.Tilt.{prefName}"

	@objc.python_method
	def pref(self, prefName):
		return float(Glyphs.defaults[self.prefDomain(prefName)])

	@objc.python_method
	def setPref(self, prefName, value):
		Glyphs.defaults[self.prefDomain(prefName)] = value

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize(MENU_NAME)

		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize(ACTION_BUTTON_LABEL)

		# default values, also needed when called through a Custom Parameter without values
		Glyphs.registerDefault(self.prefDomain("angle"), 0.0)
		Glyphs.registerDefault(self.prefDomain("tilt"), 10.0)

		# Vanilla dialog: needs a window, but only its group’s NSView is used.
		# The width leaves room for the gear menu and the buttons Glyphs adds below the view.
		width = 320
		inset = 15
		fieldLeft = 110
		fieldWidth = 70
		height = 76
		self.paletteView = Window((width, height))
		self.paletteView.group = Group((0, 0, width, height))
		group = self.paletteView.group

		group.angleLabel = TextBox((inset, 15, fieldLeft - inset - 5, 17), Glyphs.localize(ANGLE_LABEL))
		group.angleField = EditText((fieldLeft, 12, fieldWidth, 22), "", callback=self.valueChanged)
		group.angleUnit = TextBox((fieldLeft + fieldWidth + 5, 15, 15, 17), "°")
		group.angleLabel.setToolTip(Glyphs.localize(ANGLE_TOOLTIP))
		group.angleField.setToolTip(Glyphs.localize(ANGLE_TOOLTIP))

		group.tiltLabel = TextBox((inset, 45, fieldLeft - inset - 5, 17), Glyphs.localize(TILT_LABEL))
		group.tiltField = EditText((fieldLeft, 42, fieldWidth, 22), "", callback=self.valueChanged)
		group.tiltUnit = TextBox((fieldLeft + fieldWidth + 5, 45, 15, 17), "°")
		group.tiltLabel.setToolTip(Glyphs.localize(TILT_TOOLTIP))
		group.tiltField.setToolTip(Glyphs.localize(TILT_TOOLTIP))

		self.dialog = group.getNSView()

	# On dialog show
	@objc.python_method
	def start(self):
		group = self.paletteView.group
		group.angleField.set(f"{self.pref('angle'):g}")
		group.tiltField.set(f"{self.pref('tilt'):g}")

	# Action triggered by UI
	@objc.python_method
	def valueChanged(self, sender):
		group = self.paletteView.group
		values = {}
		for prefName, field in (("angle", group.angleField), ("tilt", group.tiltField)):
			try:
				values[prefName] = float(field.get().replace(",", "."))
			except ValueError:
				return  # incomplete input like "" or "-": keep the last valid preview
		for prefName, value in values.items():
			self.setPref(prefName, value)
		self.update()

	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):

		# Called on font export, get values from customParameters,
		# otherwise use the values stored from the dialog
		angle = float(customParameters.get("angle", self.pref("angle")))
		tilt = float(customParameters.get("tilt", self.pref("tilt")))

		decomposedLayer = layer.copyDecomposedLayer()
		if not decomposedLayer.shapes:
			return

		bounds = decomposedLayer.bounds
		center = NSPoint(
			bounds.origin.x + bounds.size.width * 0.5,
			bounds.origin.y + bounds.size.height * 0.5,
		)
		distance = 2.0 * max(bounds.size.width, bounds.size.height)
		if not distance:
			return

		for path in decomposedLayer.paths:
			for node in path.nodes:
				node.position = tiltedPosition(node.position, center, angle, tilt, distance)
		for anchor in layer.anchors:
			anchor.position = tiltedPosition(anchor.position, center, angle, tilt, distance)

		layer.shapes = copy.copy(decomposedLayer.shapes)

	@objc.python_method
	def generateCustomParameter(self):
		return "%s; angle:%s; tilt:%s;" % (
			self.__class__.__name__,
			self.pref("angle"),
			self.pref("tilt"),
		)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
