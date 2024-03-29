import psycopg2
from psycopg2.extras import RealDictCursor

import app.api.base.base_errors as errors
from app.config.config import DATABASE


class Sql:
    @staticmethod
    def connect():
        config_connect = "dbname='{dbname}' user='{user}' host='{host}' password='{password}'"
        connect = psycopg2.connect(config_connect.format(**DATABASE))
        return connect, connect.cursor(cursor_factory=RealDictCursor)

    @staticmethod
    def exec(query=None, args=None, file=None):
        return Sql._switch(query=query, args=args, file=file)

    @staticmethod
    def _switch(query=None, args=None, file=None):
        if query and args:
            return Sql._query_exec_args(query, args)
        if query and not args:
            return Sql._query_exec(query)
        if file and args:
            return Sql._query_file_args_exec(file, args)
        if file:
            return Sql._query_file_exec(file)
        return errors.SQL_ERROR

    @staticmethod
    def _query_exec(query):
        return Sql._exec(query)

    @staticmethod
    def _query_file_exec(file):
        with open(file, 'r') as f:
            query = f.read()
            return Sql._exec(query)

    @staticmethod
    def _query_file_args_exec(file, args):
        with open(file, 'r') as f:
            query = f.read().format(**args)
            return Sql._exec(query)

    @staticmethod
    def _query_exec_args(query, args):
        for k, v in args.items():
            alert_items = ["'", '"', ';', '-', '*', 'drop', 'select', '=', 'insert']
            if isinstance(v, str):
                for alert in alert_items:
                    if alert in v:
                        args[k] = args[k].replace(alert, '')
        query = query.format(**args)
        print(query)
        return Sql._exec(query)

    @staticmethod
    def _exec(query):
        """
        Метод выполняет SQL запрос к базе
        :param query: str SQL запрос
        :return: dict результат выполнения запроса
        """
        connect, current_connect = Sql.connect()
        current_connect.autocommit = True
        result = None
        try:
            current_connect.execute(query)
            connect.commit()
        except psycopg2.Error as e:
            print(e.pgerror)
            print(e.diag.message_primary)
            print(psycopg2.errorcodes.lookup(e.pgcode))
        finally:
            try:
                result = current_connect.fetchall()
            except:
                pass
            finally:
                connect.close()
                return result
