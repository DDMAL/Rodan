from django.conf.urls import url, patterns

urlpatterns = patterns('rodan.jobs.neon.neon_handler',
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/revert$', 'revert_file'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/insert/neume$', 'insert_neume'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/move/neume$', 'move_neume'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/delete/neume$', 'delete_neume'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/update/neume/headshape', 'update_neume_head_shape'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/neumify$', 'neumify'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/ungroup$', 'ungroup'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/insert/division$', 'insert_division'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/move/division$', 'move_division'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/delete/division$', 'delete_division'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/insert/dot$', 'insert_dot'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/delete/dot$', 'delete_dot'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/insert/clef$', 'insert_clef'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/move/clef$', 'move_clef'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/update/clef/shape$', 'update_clef_shape'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/delete/clef$', 'delete_clef'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/insert/custos$', 'insert_custos'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/move/custos$', 'move_custos'),
    url(r'^(?P<runjob_id>[0-9a-z\-]+)/delete/custos$', 'delete_custos')
)
