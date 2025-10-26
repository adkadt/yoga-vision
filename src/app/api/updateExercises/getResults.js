import { NextResponse } from 'next/server';
import { query } from '../../lib/db';

export async function GET(request) {
  try {
    const sql = `
      SELECT exercises, status, score FROM exercises
    `;
    
    const result = await query(sql, exercises);
    
    return NextResponse.json({ 
      message: "Data Fetched", 
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