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
    items ---------> text ---------> topics

      ^                                |
      |             .----.             |
      |            (      )            |
      |            |~----~|            |
      +----------  |  DB  | <----------+
                    ~----~

This is global to the whole database.

[logo]: http://i.imgur.com/TmHKI.png
