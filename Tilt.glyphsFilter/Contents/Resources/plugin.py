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
#	Both values accept a range like 10:30 for a random value in between, new for each layer.
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter
#
#	Copyright Rainer Erich Scheichelbauer (@mekkablue)
#	Licensed under the Apache License, Version 2.0, see LICENSE.
#
#
###########################################################################################################

import objc
from math import ceil, radians, sin, cos
from random import uniform
from AppKit import NSFontAttributeName, NSString
from Foundation import NSPoint
from GlyphsApp import Glyphs
from GlyphsApp.plugins import FilterWithDialog
from GlyphsApp.UI import SteppingEditText
from vanilla import Window, Group, TextBox

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
	"en": "Angle (ccw, 0=north)",
	"de": "Winkel (ggUZS, 0=Nord)",
	"fr": "Angle (antihoraire, 0=nord)",
	"it": "Angolo (antiorario, 0=nord)",
	"pt": "Ângulo (anti-horário, 0=norte)",
	"es": "Ángulo (antihorario, 0=norte)",
	"ko": "각도 (반시계, 0=북쪽)",
	"cs": "Úhel (proti hod. r., 0=sever)",
	"ja": "角度（反時計回り、0=北）",
	"zh-Hans": "角度（逆时针，0=北）",
	"zh-Hant": "角度（逆時針，0=北）",
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
	"en": "Tilt of plane",
	"de": "Kippung der Ebene",
	"fr": "Inclinaison du plan",
	"it": "Inclinazione del piano",
	"pt": "Inclinação do plano",
	"es": "Inclinación del plano",
	"ko": "평면 기울기",
	"cs": "Náklon roviny",
	"ja": "平面の傾き",
	"zh-Hans": "平面倾斜度",
	"zh-Hant": "平面傾斜度",
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

RANGE_HINT = {
	"en": "Two numbers with a colon (e.g. 10:30) give a random value in between, new for each glyph.",
	"de": "Zwei Zahlen mit Doppelpunkt (z. B. 10:30) ergeben einen Zufallswert dazwischen, neu für jedes Glyph.",
	"fr": "Deux nombres séparés par deux-points (p. ex. 10:30) donnent une valeur aléatoire entre les deux, nouvelle pour chaque glyphe.",
	"it": "Due numeri separati da due punti (es. 10:30) danno un valore casuale compreso tra i due, nuovo per ogni glifo.",
	"pt": "Dois números separados por dois-pontos (p. ex. 10:30) geram um valor aleatório entre eles, novo para cada glifo.",
	"es": "Dos números separados por dos puntos (p. ej. 10:30) dan un valor aleatorio entre ambos, nuevo para cada glifo.",
	"ko": "콜론으로 구분한 두 숫자(예: 10:30)는 그 사이의 무작위 값이며 글리프마다 새로 정해집니다.",
	"cs": "Dvě čísla oddělená dvojtečkou (např. 10:30) dají náhodnou hodnotu mezi nimi, pro každý glyf novou.",
	"ja": "コロンで区切った2つの数値（例：10:30）は、その間のランダムな値になり、グリフごとに新しく決まります。",
	"zh-Hans": "用冒号分隔的两个数字（如 10:30）表示两者之间的随机值，每个字形各取一次。",
	"zh-Hant": "以冒號分隔的兩個數字（如 10:30）表示兩者之間的隨機值，每個字形各取一次。",
}


def parseRange(text):
	"""
	Returns (low, high) as floats for text like "10" (low = high = 10.0)
	or "10:30" (a range, also written "10~30" in Custom Parameters, where the colon is taken).
	Raises ValueError for incomplete or invalid input.
	"""
	parts = str(text).strip().replace(",", ".").replace("~", ":").split(":")
	if len(parts) == 1:
		return float(parts[0]), float(parts[0])
	if len(parts) == 2:
		return float(parts[0]), float(parts[1])
	raise ValueError("not a number or a range: %s" % text)


def customParameterValue(text):
	"""Writes a dialog value for a Custom Parameter: no colon (it separates name and value), no spaces."""
	return str(text).strip().replace(",", ".").replace(" ", "").replace(":", "~")


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
		return str(Glyphs.defaults[self.prefDomain(prefName)])

	@objc.python_method
	def setPref(self, prefName, value):
		Glyphs.defaults[self.prefDomain(prefName)] = value

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize(MENU_NAME)

		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize(ACTION_BUTTON_LABEL)

		self.buildDialog()

	@objc.python_method
	def registerDefaults(self):
		# default values (strings, because they may be ranges), also needed when called
		# through a Custom Parameter without values
		Glyphs.registerDefault(self.prefDomain("angle"), "0")
		Glyphs.registerDefault(self.prefDomain("tilt"), "10")

	@objc.python_method
	def buildDialog(self):
		"""
		Vanilla dialog: needs a window, but only its group’s NSView is used.
		Safe to call more than once: Glyphs also asks for the view of instances on which settings()
		has not run, e.g. in the Custom Parameter dialog, so view() builds the dialog on demand.
		"""
		if getattr(self, "paletteView", None) is not None:
			return
		self.registerDefaults()

		# The width leaves room for the gear menu and the buttons Glyphs adds below the view.
		width = 400
		height = 76
		inset = 15
		gap = 4
		self.paletteView = Window((width, height))
		self.paletteView.group = Group((0, 0, width, height))
		group = self.paletteView.group
		rangeHint = Glyphs.localize(RANGE_HINT)
		angleTooltip = f"{Glyphs.localize(ANGLE_TOOLTIP)} {rangeHint}"
		tiltTooltip = f"{Glyphs.localize(TILT_TOOLTIP)} {rangeHint}"

		# Right-aligned labels, as wide as the widest one, butting against the fields,
		# which take the rest of the width up to the right edge.
		group.angleLabel = TextBox((inset, 15, 100, 17), Glyphs.localize(ANGLE_LABEL), alignment="right")
		group.tiltLabel = TextBox((inset, 45, 100, 17), Glyphs.localize(TILT_LABEL), alignment="right")
		labelWidth = ceil(max(self.textWidth(group.angleLabel), self.textWidth(group.tiltLabel))) + 4  # cell padding
		group.angleLabel.setPosSize((inset, 15, labelWidth, 17))
		group.tiltLabel.setPosSize((inset, 45, labelWidth, 17))
		fieldLeft = inset + labelWidth + gap

		group.angleField = SteppingEditText((fieldLeft, 12, -inset, 22), "", callback=self.valueChanged)
		group.tiltField = SteppingEditText((fieldLeft, 42, -inset, 22), "", callback=self.valueChanged)
		for element, tooltip in (
			(group.angleLabel, angleTooltip),
			(group.angleField, angleTooltip),
			(group.tiltLabel, tiltTooltip),
			(group.tiltField, tiltTooltip),
		):
			element.setToolTip(tooltip)

		self.dialog = group.getNSView()

		# The Custom Parameter dialog stacks the view with Auto Layout and takes its height from
		# constraints, so a view with only frame-based content would collapse to zero height there.
		self.dialog.heightAnchor().constraintEqualToConstant_(height).setActive_(True)
		self.loadValues()

	@objc.python_method
	def textWidth(self, textBox):
		nsTextField = textBox.getNSTextField()
		attributes = {NSFontAttributeName: nsTextField.font()}
		return NSString.stringWithString_(nsTextField.stringValue()).sizeWithAttributes_(attributes).width

	def view(self):
		self.buildDialog()
		return self.dialog

	@objc.python_method
	def loadValues(self):
		group = self.paletteView.group
		group.angleField.set(self.pref("angle"))
		group.tiltField.set(self.pref("tilt"))

	# On dialog show
	@objc.python_method
	def start(self):
		self.loadValues()

	# Action triggered by UI
	@objc.python_method
	def valueChanged(self, sender):
		group = self.paletteView.group
		values = {}
		for prefName, field in (("angle", group.angleField), ("tilt", group.tiltField)):
			text = field.get().strip()
			try:
				parseRange(text)
			except ValueError:
				return  # incomplete input like "", "-" or "10:": keep the last valid preview
			values[prefName] = text
		for prefName, text in values.items():
			self.setPref(prefName, text)

		# the Custom Parameter dialog has no layers to preview
		if self.valueForKey_("layers") is not None:
			self.update()

	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):

		# Called on font export, get values from customParameters,
		# otherwise use the values stored from the dialog.
		# A range like 10:30 (10~30 in Custom Parameters) gets a new random value for each layer.
		angleLow, angleHigh = parseRange(customParameters.get("angle", self.pref("angle")))
		tiltLow, tiltHigh = parseRange(customParameters.get("tilt", self.pref("tilt")))
		angle = uniform(angleLow, angleHigh)
		tilt = uniform(tiltLow, tiltHigh)

		# Work on a copy with all components decomposed (corner components included),
		# without hints, so they cannot interfere with the moved nodes. The layer loses its hints, too.
		workLayer = layer.copyDecomposedLayer()
		workLayer.hints = None
		workLayer.cleanUpPaths()  # e.g. duplicate nodes at start points left over from decomposing
		if not workLayer.shapes:
			return

		bounds = workLayer.bounds
		center = NSPoint(
			bounds.origin.x + bounds.size.width * 0.5,
			bounds.origin.y + bounds.size.height * 0.5,
		)
		distance = 2.0 * max(bounds.size.width, bounds.size.height)
		if not distance:
			return

		for path in workLayer.paths:
			for node in path.nodes:
				node.position = tiltedPosition(node.position, center, angle, tilt, distance)

		# anchors stay on the layer, only their positions change
		for anchor in layer.anchors:
			anchor.position = tiltedPosition(anchor.position, center, angle, tilt, distance)

		# hints would point to nodes that are about to be replaced
		layer.hints = None
		layer.shapes = workLayer.shapes

	@objc.python_method
	def generateCustomParameter(self):
		return "%s; angle:%s; tilt:%s;" % (
			self.__class__.__name__,
			customParameterValue(self.pref("angle")),
			customParameterValue(self.pref("tilt")),
		)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
