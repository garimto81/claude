/**
 * 전체 마이그레이션 한 번에 실행
 */

import { Client } from 'pg'
import { readFileSync } from 'fs'
import { join } from 'path'
import * as dotenv from 'dotenv'

dotenv.config({ path: '.env.local' })

const DATABASE_URL = process.env.DATABASE_URL

if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL not found')
  process.exit(1)
}

async function runAllMigrations() {
  const client = new Client({ connectionString: DATABASE_URL })

  try {
    console.log('\n🔌 Connecting to Supabase...')
    await client.connect()
    console.log('   ✅ Connected!')

    console.log('\n📄 Reading all-migrations-fixed.sql...')
    const sql = readFileSync(join(process.cwd(), 'supabase', 'all-migrations-fixed.sql'), 'utf-8')

    console.log('\n⚡ Executing all migrations...')
    await client.query(sql)

    console.log('\n✅ All migrations executed successfully!')
    console.log('\n📝 Next: Create admin user in Supabase Dashboard')
    console.log('   Email: admin@example.com')
    console.log('   Password: Admin1234!')
    console.log('')

  } catch (error: any) {
    console.error('\n❌ Error:', error.message)
    console.error('\nDetails:', error.detail || error)
    process.exit(1)
  } finally {
    await client.end()
  }
}

runAllMigrations()
