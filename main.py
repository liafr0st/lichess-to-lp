import requests
import argparse
import re

def getMatchLength(moves: str) -> int:
    moveNos = re.findall(r"[0-9]+\. ",moves)
    l = moveNos[-1][:-2]
    return int(l)

def getLichessStudy(studyId: str) -> str:
    response = requests.get(f"https://lichess.org/api/study/{studyId}.pgn")
    return response.text

def parseLichessStudy(pgn: str):
    pgns = pgn.split("\n\n\n")
    matches = {}
    for match in pgns:
        lines = match.split("\n")
        try:
            matchName = re.search(r"\[[a-zA-Z]* \"(.*)\"\]",lines[0]).group(1)
        except AttributeError:
            continue
        matches[matchName] = {}
        for line in lines:
            if line.startswith("["):
                r = re.search(r"\[([a-zA-Z]*) \"(.*)\"\]",line)
                attr, value = r.group(1), r.group(2)
                matches[matchName][attr] = value
        matches[matchName]["Length"] = getMatchLength(lines[-1])

    return matches

def generateWikicode(parsedPgns) -> str:
    finalStr = ""
    for match in parsedPgns.values():
        white = " ".join(reversed(match["White"].split(", ")))
        black = " ".join(reversed(match["Black"].split(", ")))
        finished = "true"
        if match.get("Result")=="1-0":
            winner=1
        elif match.get("Result")=="0-1":
            winner=2
        elif match.get("Result")=="1/2-1/2":
            winner=0
        else:
            finished=""
        matchStr = \
"""|{{Match
    |date={{\\#var:rounddate}}
    |finished=%s
    |opponent1={{1Opponent|%s|flag=}}
    |opponent2={{1Opponent|%s|flag=}}
    |map1={{Map|white=1|eco=%s|length=%d|winner=%d
        |chesscom=
        |lichess=%s
    }}
}}
""" % (finished, white, black, match.get("ECO"), match.get("Length"), winner, match.get("Site"))
        finalStr += matchStr
    return finalStr

def writeWikicode(wikicode: str, filename: str) -> None:
    with open(filename,"w") as file:
        file.write(wikicode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pgn")
    parser.add_argument("-f", "--file")
    args = parser.parse_args()

    roundPgn = getLichessStudy(args.pgn)
    matches = parseLichessStudy(roundPgn)
    wikicode = generateWikicode(matches)
    if args.file:
        writeWikicode(wikicode,args.file)

    return 0


if __name__ == "__main__":
    main()