ratings = [];
r = open("ratings.txt","r");
line = "";
while True:
    line = r.readline();
    if len(line) == 0:
        break;
    ratings.append(line.strip().split("|"));
r.close();

orderedRatings = [];
curRating = 10.0;
while curRating >= 0:
    for rating in ratings:
        if rating[1] == str(curRating):
            orderedRatings.append(rating);
    curRating -= 0.1;

for rating in orderedRatings:
    print rating