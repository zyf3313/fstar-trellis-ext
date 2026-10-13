# MySQL conventions

**Trigger:** Project declares MySQL. MariaDB has its own profile.

Confirm actual MySQL server version, SQL mode, collation/time zone, keys/constraints and InnoDB transaction boundaries. DDL may implicitly commit; design recovery accordingly. Parameter bindings follow the real driver. Server max_execution_time for SELECT does not prove DML cancellation; verify unknown write results before retry. Source: https://dev.mysql.com/doc/ .
