#ifndef CARD_H
#define CARD_H

#include <iostream>
#include <string>

static const char *szinek[4] = { "tok", "makk", "piros", "zold" };
static const char *kepek[8]  = { "VII", "VIII", "IX", "X", "also", "felso", "kiraly", "asz" };

struct Card {

	typedef enum { TOK, MAKK, PIROS, ZOLD } Szin;

	typedef enum { VII, VIII, IX, X, ALSO, FELSO, KIRALY, ASZ } Kep;

	Card() = default;
	constexpr Card(Card::Szin szin, Card::Kep kep)
		: szin(szin), kep(kep) {};

	Szin szin;
	Kep kep;

	bool operator==(Card const &other) const {
		return other.szin == szin && other.kep == kep;
	}

	bool operator!=(Card const &other) const {
		return !(*this == other);
	}

	operator std::string() const {
		std::string ez_szin = szinek[szin];	
		std::string ez_kep = kepek[kep];	
		return ez_szin + ' ' + ez_kep;
	}

	friend std::ostream &operator<<(std::ostream &out, Card card) {
		return out << std::string(card);
	}

};

#endif
