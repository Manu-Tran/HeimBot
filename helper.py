#!/usr/bin/env python3
#
import re
import random

#Infos à garder up tout le temps, surtout le dictionnaire des joueurs qui garde le death count en mémoire.
death_phrases = [" died like a lil' bitch", " got rekt.", " a découvert le sens de l'expression \'6 pieds sous terre\'", " ahahahahahahahaha.", " est parti rejoindre ses grands morts.", "... CHEH!", " a fait une Drim.", " n'a pas couru assez vite.", " git gud.", "... Tu sais que le death count n'est pas un kikimeter?", " va encore dire que c'est la faute du lag.", "... Sans commentaires.", ", c'était pathétique.", " n'a plus de skills, littéralement.", " est mort. Je suis sûr qu'il voulait juste se tp à son lit.", " IS NOT WORTHY!", " pourrait essayer de jouer avec autre que ses pieds.", "... Allume l'écran stp.", "... Tu sais que pour aller au Valhalla il faut une mort glorieuse ?", " nourrit les poissons.", " a été aussi mauvais que Delmas sur Smash"]

#Passe la structure players et la ligne de log à analyser
def parse_line(state, line: str, players) -> None:
    match = re.search("Got\scharacter\sZDOID\sfrom\s([\w\d]{1,})\s:\s(-?\d{1,}:-?\d{1,})",line)
    if(match):
        if(match.group(2) == '0:0'):
            death_count = state.inc_death_count(match.group(1))
            players[match.group(1)] = [0,death_count]
            return str(match.group(1) + death_phrases[random.randint(0,len(death_phrases)-1)] + "\n(Death count: " + str(death_count) + ")")
        else:
            if(match.group(1) in players):
                if(players[match.group(1)][0] == 0):
                    players[match.group(1)] = [1,players[match.group(1)][1]]
                    return ""
                else:
                    return str(match.group(1) + " HAS ARRIVED")
            else:
                players[match.group(1)] = [1,0]
                return str(match.group(1) + " HAS ARRIVED")
    else:
        match = re.search("Closing socket (.*)", line)
        if match and match.group(1) != "0":
            return("A player has left !")
        else:
            return ""

def verify_date(date: str) -> bool:
    try:
        match = re.search('([0-9]{4})/([0-9]{2})/([0-9]{2})-([0-9]{2}):([0-9]{2}):([0-9]{2})', date)
        return (match
            and int(match.group(2)) <= 12
            and int(match.group(3)) <= 31
            and int(match.group(4)) <= 24
            and int(match.group(5)) < 60
            and int(match.group(6)) < 60)
    except ValueError:
        return False

def get_next_offset(line: str) -> str:
    match = re.search('([0-9]{2})/([0-9]{2})/([0-9]{4}) ([0-9]{2}):([0-9]{2}):([0-9]{2})', line)
    if match:
        return "%s/%s/%s-%s:%s:%s" % (match.group(3),
                                        match.group(1),
                                        match.group(2),
                                        match.group(4),
                                        match.group(5),
                                        match.group(6))
    else :
        return ""
