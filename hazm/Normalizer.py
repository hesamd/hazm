#coding=utf8

import re
from .utils import u
maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))
compile_patterns = lambda patterns: [(re.compile(u(pattern)), repl) for pattern, repl in patterns]


class Normalizer():
	def __init__(self):
		self.translations = maketrans(u('كي%1234567890'), u('کی٪۱۲۳۴۵۶۷۸۹۰'))

		punc_after, punc_before = r'!:\.،؛؟»\]\)\}', r'«\[\(\{'
		self.character_refinement_patterns = compile_patterns([
			(r'[ ]+', ' '), # extra spaces
			(r'[\n\r]+', '\n'), # extra newlines
			(r'ـ+', ''), # keshide
		])

		self.punctuation_spacing_patterns = compile_patterns([
			(' (['+ punc_after +'])', r'\1'), # remove space before
			('(['+ punc_before +']) ', r'\1'), # remove space after
			('(['+ punc_after +'])([^ '+ punc_after +'])', r'\1 \2'), # put space after
			('([^ '+ punc_before +'])(['+ punc_before +'])', r'\1 \2'), # put space before
		])

		self.affix_spacing_patterns = compile_patterns([
			(r'([^ ]ه) ی ', r'\1‌ی '), # fix ی space
			(r' (ن?می) ', r' \1‌'), # put zwnj after می, نمی
			(r' (تر(ی(ن)?)?|ها(ی)?) ', r'‌\1 '), # put zwnj before تر, ترین, ها, های
		])

	def normalize(self, text):
		text = self.character_refinement(text)
		text = self.punctuation_spacing(text)
		text = self.affix_spacing(text)
		return text

	def character_refinement(self, text):
		"""
		>>> print(normalizer.character_refinement('اصلاح كاف و ياي عربي'))
		اصلاح کاف و یای عربی

		>>> print(normalizer.character_refinement('رمــــان'))
		رمان
		"""

		text = text.translate(self.translations)
		for pattern, repl in self.character_refinement_patterns:
			text = pattern.sub(repl, text)
		return text

	def punctuation_spacing(self, text):
		"""
		>>> print(normalizer.punctuation_spacing('اصلاح ( پرانتزها ) در متن .'))
		اصلاح (پرانتزها) در متن.
		"""

		# todo: don't put space inside time and float numbers
		for pattern, repl in self.punctuation_spacing_patterns:
			text = pattern.sub(repl, text)
		return text

	def affix_spacing(self, text):
		"""
		>>> print(normalizer.affix_spacing('خانه ی پدری'))
		خانه‌ی پدری

		>>> print(normalizer.affix_spacing('فاصله میان پیشوند ها و پسوند ها را اصلاح می کند.'))
		فاصله میان پیشوند‌ها و پسوند‌ها را اصلاح می‌کند.
		"""

		for pattern, repl in self.affix_spacing_patterns:
			text = pattern.sub(repl, text)
		return text


if __name__ == '__main__':
	import doctest
	doctest.testmod(extraglobs={'normalizer': Normalizer()})
