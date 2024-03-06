# Copyright (C) 2018  danielwine/Daniel Vinkovics

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation (version 3)

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import re

import wikiquote
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

__author__ = 'danielwine'


class WikiQuoteSkill(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude_list = ['ISBN', 'Citatum']

    def getRandomQuote(self,
                       titles,
                       mostRelevant=False,
                       length=4,
                       filterYear=True):
        quote = None
        quotes = None
        match = None
        counter = 0
        max_sentences = length
        while quote is None or len(quote.split('.')) > max_sentences:
            counter += 1
            if not mostRelevant:
                title = random.choice(titles)
            else:
                title = titles[0]
            try:
                quotes = wikiquote.quotes(title, lang=self.lang.split('-')[0])
            except wikiquote.utils.DisambiguationPageException:
                quotes = None
            if quotes and quotes != []:
                quote = random.choice(quotes)
                if filterYear: 
                    match = re.match('.*([1-3][0-9]{3})', quote)
                if match: 
                    quote = None
                for word in self.exclude_list:
                    if quote and word in quote: quote = None
            if counter > 5: quote = ''
        return quote, title

    @intent_handler('specific.intent')
    def handle_specific_quote_intent(self, message):
        subject = message.data.get('subject')
        results = wikiquote.search(subject, lang=self.lang.split('-')[0])
        if len(results) == 0:
            self.speak_dialog("notfound", {'subject': subject})
        else:
            quote, title = self.getRandomQuote(results,
                                               mostRelevant=True,
                                               length=10,
                                               filterYear=False)
            if quote == '':
                self.speak_dialog("notfound", {'subject': subject})
            else:
                self.speak(quote + ' (' + title + ')')

    @intent_handler('random.intent')
    def handle_random_quote_intent(self, message):
        randomtitles = []
        while randomtitles is None or randomtitles == []:
            randomtitles = wikiquote.random_titles(lang=self.lang.split('-')[0])
        quote, title = self.getRandomQuote(randomtitles)
        self.speak(quote + ' (' + title + ')')
