
import { query } from '././lib/db';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({message: "Method not allowed"});
    }

    const { exercises } = req.body;

    if (!Array.isArray(exercises) || exercises.length === 0) {
        return res.status(400).json({message: 'No exercises provided'});
    }

    try {
        const placeholders = exercises.map(() => '?').join(', ');
        
        const sql = `
        UPDATE exercises_table
        SET enabled = 1,
        status = 1,
        user_selection = 1
        WHERE exercises IN (${placeholders})
        `;

        const result = await query(sql, exercises);

        res.status(200).json({ message: "Exercises updated", affectedRows: result.affectedRows});

    }
    catch (err) {
        console.error(err);
        res.status(500).json({ message: "Database error", error: err.message});
    }
}