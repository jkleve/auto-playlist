from api import create_app, run_app

__author__ = 'Jesse Kleve'
__version__ = '0.9.0'


def main():
    run_app(create_app())

if __name__ == '__main__':
    main()
