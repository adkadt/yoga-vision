import { NextResponse } from 'next/server';
import { query } from '../../lib/db';

export async function POST(request) {
  try {
    const { exercises } = await request.json();
    
    if (!Array.isArray(exercises) || exercises.length === 0) {
      return NextResponse.json(
        { message: 'No exercises provided' },
        { status: 400 }
      );
    }
    
    const placeholders = exercises.map(() => '?').join(', ');
    const sql = `
      UPDATE exercises
      SET enabled = 1,
          status = 1,
          user_selection = 1
      WHERE exercise IN (${placeholders})
    `;
    
    const result = await query(sql, exercises);
    
    return NextResponse.json({ 
      message: "Exercises updated", 
      affectedRows: result.affectedRows 
    });
    
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { message: "Database error", error: err.message },
      { status: 500 }
    );
  }
}