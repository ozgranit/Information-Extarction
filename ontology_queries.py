import rdflib

ontology = rdflib.Graph()
ontology.parse("ontology.nt", format="nt")
prefix = "http://example.org/"


def query_a(file):
    print("a: Premier League Brasilian players and their Teams name:\n")
    file.write("a: Premier League Brasilian players and their Teams name:\r\n")
    q = "select ?p ?t where { ?p <"+prefix+"birthPlace> ?c ." \
        " ?c <"+prefix+"located_in> <"+prefix+"Brazil> ." \
        " ?p <"+prefix+"playsFor> ?t} "
    x1 = ontology.query(q)
    for line in list(x1):
        print(line)
        file.write("\t" + str(line) + "\r\n")
    print("total a's:", len(x1), "\n")
    file.write("total a's:" + str(len(x1)) + "\r\n")


def query_b(file):
    print("b: Premier League players born after 1995 and their Teams name:\n")
    file.write("b: Premier League players born after 1995 and their Teams name:\r\n")
    q = "select ?p ?t where { ?p <"+prefix+"birthDate> ?date ." \
        " ?p <"+prefix+"playsFor> ?t . " \
        "FILTER (?date >= \"1995-01-01\"^^xsd:date)} "
    x1 = ontology.query(q)
    for line in list(x1):
        print(line)
        file.write("\t" + str(line) + "\r\n")
    print("total b's:", len(x1), "\n")
    file.write("total b's:" + str(len(x1)) + "\r\n")


def query_c(file):
    print("c: Premier League players that play for their Hometoun:\n")
    file.write("c: Premier League players that play for their Hometoun:\r\n")
    q = "select ?p where { ?p <"+prefix+"birthPlace> ?c . " \
        "?p <"+prefix+"playsFor> ?t ." \
        "?t <"+prefix+"homeCity> ?c}"
    x1 = ontology.query(q)
    for line in list(x1):
        print(line)
        file.write("\t" + str(line) + "\r\n")
    print("total c's:", len(x1), "\n")
    file.write("total c's:" + str(len(x1)) + "\r\n")


def query_d(file):
    print("d: All possible Derby combination:\n")
    file.write("d: All possible Derby combination:\r\n")
    q = "select distinct ?t1 ?t2 where {" \
        "?t1 <"+prefix+"homeCity> ?c1 ." \
        "?t2 <"+prefix+"homeCity> ?c2 ." \
        "FILTER (?c1 = ?c2 && ?t1!=?t2 && STR(IRI(?t1)) < STR(IRI(?t2)))}"
    x1 = ontology.query(q)
    for line in list(x1):
        print(line)
        file.write("\t" + str(line) + "\r\n")
    print("total d's:", len(x1), "\n")
    file.write("total d's:" + str(len(x1)) + "\r\n")


if __name__ == "__main__":
    print("running...")
    f = open("question2c.txt", "w+", encoding="utf-8")
    print("Getting 2c answers from 'ontology.nt': \n")
    f.write("Getting 2c answers from 'ontology.nt': \r\n")

    query_a(f)
    query_b(f)
    query_c(f)
    query_d(f)

    f.close()

    print("done.")

