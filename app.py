from website.app import create_app


app = create_app({
  'SECRET_KEY': 'secret'
})
