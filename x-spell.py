#!/usr/bin/env vpython3
import hunspell

topdir='/usr/share/hunspell'
lang = 'en_US'

hobj = hunspell.HunSpell('{}/{}.dic'.format(topdir, lang), '{}/{}.aff'.format(topdir, lang))
for word in (
    'spookie',
    'spooky'
):
    result = hobj.spell(word)
    print('spell({})={}'.format(word, result))
    suggest = hobj.suggest(word)
    print('suggest:', suggest)
