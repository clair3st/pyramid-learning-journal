import os
import sys
import transaction
from datetime import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import Entry


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=title]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    ENTRIES = [
        {"title": "Jinja2 Templates and Binary Heap",
         "id": 1,
         "creation_date": "Dec 20, 2016",
         "body": "Pyramid, jinja2, binary heap, prepping for my lightning talk. Kudos to those who can get everything to work, and can complete every assignment on-time. Well, that's not me. Struggled with the jinja2 and passing the id correctly to bring up the correct article. And that was with Rachael, Ben, and Will's help. Working with Ted on the Binary Heap was great, but I wasn't able to finish doing all of the tests. Excited to learn with my project team how to scrape and then assemble info off 3rd party sites. Coming from the SEO world, I know of black hats who use scraping to aggregate content, change it slightly, and then re-publish it as their own content. At this hour, I guess the question is sleep or work."},
        {"title": "Pyramid Framework",
         "id": 2,
         "creation_date": "Dec 19, 2016",
         "body": "TIL, Git is a still an issue for me at times. (Go, go Patrick's Git idea). I also learned if you make a mistake early in the setup of a long process in class, there's no way to catch up, and you're better off just watching what Nick does and take good notes (see Pyramid/Heroku setups). I re-learned about checking for which python version you use. I learned I still hate CSS (there's no CSS in Python, once said by one sage instructor). The pyramid framework was more rote learning, and probably the easiest part of the 2nd assignment. The complication about how you setup your files and repo, that caused all the pain."},
        {"title": "HTTP Server",
         "id": 3,
         "creation_date": "Dec 16, 2016",
         "body": "os.path to determine absolute path, listdir, mimetype detection, detect whether a file or a directory... I learned a lot in lab today on the http server project, despite the rabbit holes and complete refactoring needing to be done halfway through, and still way behind. It's tough with missing team members, who then come back and aren't as up to speed - especially when you're scrambling and under the gun to accomplish so much in a day, and not get even further behind. This weekend is gonna be a doozy. We also learned concurrency and asynchronous connections in class - I think we get to use that today."},
        {"title": "A Day of Catch-Up",
         "id": 4,
         "creation_date": "Dec 22, 2016",
         "body": "Got my learning journal to work, including how to pass the id to the detail page and edit page. Also, when the edit is submitted, it's saved and shown on the home page. Very cool. Also, with Ben's help, finally got Heroku to work for me. My requirements.txt was messed up, as was another file. Was able to give my crontab Lightnight Talk today. 5 mins is very short (and yes, Vi is a very weird editor). The class going over Pyramid again was extremely helpful. As was no data strcture work today. I know tomorrow will be hard, so I'm trying to get to sleep before midnight tonigh, woohoo."},
        {"title": "Directional Graph, PostgreSQL, and Tests.",
         "id": 5,
         "creation_date": "Dec 23, 2016",
         "body": "Worked with Ted on the Directional Graph work. A ton of methods, but it was easier than some of the other data structures. It was fun to work with Ted all week on the data structures. He challenged me, mentored me, taught me a bunch more today, and was very thoughtful with any insights or issues. Doing tests on Step3 are hard to do, but got a db and html test to finally work. I also fixed my html/css on my learning journal site. There's only python people here at CF at 5:30pm on Dec 23rd. None of us are bothered or surprised. We're focused on tests. Happy holidays to all."}
    ]

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        for entry in ENTRIES:
            model = Entry(title=entry['title'], creation_date=datetime.strptime(entry['creation_date'], "%b %d, %Y"), body=entry['body'])
            dbsession.add(model)
