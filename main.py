from safyr.shell import Shell

def main():
    s = Shell()

if __name__ == '__main__':
    main()


# to get test coverage, type the following command in a terminal below:
# pytest --cov-report=html:cov_html --cov=. test.py
# summary results can be found in cov_html/index.html
