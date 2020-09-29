from setuptools import setup

setup(
    name='lada',
    author_email='kmsuj7@gmail.com',
    setup_requires=['libsass >= 0.6.0'],
    sass_manifests={
        'lada': {
            'sass_path': 'static/sass',
            'css_path': 'static/css',
            'wsgi_path': '/static/css',
            'strip_extension': False
        },
    }
)
