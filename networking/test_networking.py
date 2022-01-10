import pytest

from networking.client import Client

class TestConnection():
        def test_parsing(self):
            client = Client()
            queries = ["test.com", "gemini.circumlunar.space", "gemini://gemini.circumlunar.space", "testing.space/"]
            answers = ["gemini://test.com/", "gemini://gemini.circumlunar.space/", "gemini://gemini.circumlunar.space/", "gemini://testing.space/"]
            for idx in range(len(queries)):

                assert client._parse_query(queries[idx])[1] == answers[idx], "(idx: {})INCORRECTLY PARSED {}, should be: {}".format(idx, queries[idx], answers[idx])


        # TODO: This should also be a valid relative link, "gemtext.gmi"
        #
        def test_relative_parsing(self):
            client = Client()
            queries = [("test.com/test/","../"), ("gemini://test.com/docs/", "../"), ("gemini://test.com/docs/testing.gmi", "../"), ("gemini://test.com/docs/cheatsheet/testing.gmi", "../../something/else/../"), ("gemini://texto-plano.xyz/sdemingo/", "blog/index.gmi"), ("gemini://texto-plano.xyz/sdemingo/blog/index.gmi","../index.gmi")]
            answers = ["gemini://test.com/", "gemini://test.com/", "gemini://test.com/", "gemini://test.com/something/", "gemini://texto-plano.xyz/sdemingo/blog/index.gmi", "gemini://texto-plano.xyz/sdemingo/index.gmi"]

            for idx in range(len(queries)):
                parsed_query = client._parse_query(queries[idx][0], relative = queries[idx][1])[1]

                assert parsed_query == answers[idx], "(idx: {})INCORRECTLY PARSED {} into {}, should be: {}".format(idx, queries[idx], parsed_query, answers[idx])
