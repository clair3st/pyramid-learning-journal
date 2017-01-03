def includeme(config):
    config.add_static_view(name='static', path='learning_journal:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('edit', '/journal/{id:\d+}/edit')
    config.add_route('create', '/create')
    config.add_route('detail', 'journal/{id:\d+}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')