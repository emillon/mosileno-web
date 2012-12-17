![Brocoli][logo] Brocoli
========================

A collection of scripts, because celery is not enough.

Workflow
--------

### item2topics


                    topic
     web ----+      model ----+
             |                |

            tika           science
    items ---------> text ---------> itemtopics

      ^                                |
      |             .----.             |
      |            (      )            |
      |            |~----~|            |
      +----------  |  DB  | <----------+
                    ~----~

This is global to the whole database.

### topic2names

Populates `itemtopicnames` using information in `itemtopics` + hardcoded names
of topics.

    items ------> itemtopics ----> itemtopicnames

      ^                                  |
      |              .----.              |
      |             (      )             |
      |             |~----~|             |
      +-----------  |  DB  | <-----------+
                    ~----~

This is also a global pass.

### topic2scores

Populates `itemscores` for a user, given its name and its parameters.
It also re-runs tika.

This has to be run for every user.

[logo]: http://i.imgur.com/TmHKI.png
