import mariadb from 'mariadb';

const pool = mariadb.createPool({
    host: 'http://localhost',
    user: 'sql',
    password: 'knighthacks',
    database: 'yogavision',
    port: 3306,
});

export async function query (sql, params) {
    let conn;
    try {
        conn = await pool.getConnection();
        const rows = await conn.query(sql, params);
        return rows;
    }
    finally {
        if (conn) conn.release();
    }
}