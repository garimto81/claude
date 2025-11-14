/**
 * Supabase 마이그레이션 실행 스크립트 (PostgreSQL 직접 연결)
 *
 * Usage:
 *   1. Supabase Dashboard → Settings → Database → Connection String 복사
 *   2. .env.local에 DATABASE_URL 추가
 *   3. npx tsx scripts/migrate.ts
 */

import { Client } from 'pg'
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'
import * as dotenv from 'dotenv'

// 환경 변수 로드
dotenv.config({ path: '.env.local' })

const DATABASE_URL = process.env.DATABASE_URL

if (!DATABASE_URL) {
  console.error('\n❌ DATABASE_URL not found in .env.local')
  console.error('\nℹ️  Steps to get DATABASE_URL:')
  console.error('   1. Open: https://dqkghhlnnskjfwntdtor.supabase.co/project/_/settings/database')
  console.error('   2. Copy "Connection string" (URI format)')
  console.error('   3. Add to .env.local:')
  console.error('      DATABASE_URL=postgresql://postgres:[PASSWORD]@db.dqkghhlnnskjfwntdtor.supabase.co:5432/postgres')
  console.error('')
  process.exit(1)
}

/**
 * SQL 파일을 실행합니다.
 */
async function executeSqlFile(client: Client, filePath: string): Promise<void> {
  const fileName = filePath.split(/[/\\]/).pop()!
  console.log(`\n📄 Executing: ${fileName}`)

  try {
    const sql = readFileSync(filePath, 'utf-8')

    // SQL 실행
    await client.query(sql)

    console.log(`   ✅ ${fileName} completed successfully`)
  } catch (error: any) {
    console.error(`   ❌ Error in ${fileName}:`)
    console.error(`      ${error.message}`)
    throw error
  }
}

/**
 * 모든 마이그레이션을 순서대로 실행합니다.
 */
async function runAllMigrations(): Promise<void> {
  const migrationsDir = join(process.cwd(), 'supabase', 'migrations')

  console.log('\n' + '='.repeat(70))
  console.log('🚀 Supabase Database Migration')
  console.log('='.repeat(70))
  console.log('   Project: dqkghhlnnskjfwntdtor')
  console.log('   Migrations Dir:', migrationsDir)

  // PostgreSQL 클라이언트 연결
  const client = new Client({
    connectionString: DATABASE_URL,
  })

  try {
    console.log('\n🔌 Connecting to database...')
    await client.connect()
    console.log('   ✅ Connected!')

    // 마이그레이션 파일 목록 (순서대로)
    const migrationFiles = readdirSync(migrationsDir)
      .filter(file => file.endsWith('.sql'))
      .sort()

    console.log(`\n📁 Found ${migrationFiles.length} migration files`)

    let executedCount = 0
    let skippedCount = 0
    let failedCount = 0

    for (const file of migrationFiles) {
      const filePath = join(migrationsDir, file)

      // 00000_drop_all.sql은 건너뛰기 (명시적으로 실행해야 함)
      if (file.includes('drop_all')) {
        console.log(`\n⏭️  Skipping: ${file}`)
        console.log('   (Run with: npx tsx scripts/migrate.ts --drop-all)')
        skippedCount++
        continue
      }

      // 20240105_create_admin.sql도 나중에 수동 실행
      if (file.includes('create_admin')) {
        console.log(`\n⏭️  Skipping: ${file}`)
        console.log('   (Create users in Dashboard first, then run this)')
        skippedCount++
        continue
      }

      try {
        await executeSqlFile(client, filePath)
        executedCount++
      } catch (error) {
        failedCount++
        console.error(`\n❌ Failed to execute ${file}`)

        // 치명적인 에러면 중단
        if (file.includes('create_profiles') || file.includes('create_trigger')) {
          console.error('\n🛑 Critical migration failed. Stopping.')
          throw error
        }

        console.log('   ⚠️  Continuing with next migration...')
      }
    }

    console.log('\n' + '='.repeat(70))
    console.log('✅ Migration Complete!')
    console.log('='.repeat(70))
    console.log(`   ✅ Executed: ${executedCount}`)
    console.log(`   ⏭️  Skipped: ${skippedCount}`)
    console.log(`   ❌ Failed: ${failedCount}`)
    console.log('')

    if (executedCount > 0) {
      console.log('📝 Next steps:')
      console.log('   1. Create admin user in Supabase Dashboard:')
      console.log('      - Go to: Authentication → Users → Add User')
      console.log('      - Email: admin@example.com')
      console.log('      - Password: Admin1234!')
      console.log('      - ✅ Auto Confirm User')
      console.log('')
      console.log('   2. Run admin setup:')
      console.log('      npx tsx scripts/migrate.ts --create-admin')
      console.log('')
    }

  } finally {
    await client.end()
    console.log('🔌 Database connection closed.\n')
  }
}

/**
 * DROP ALL 실행 (위험!)
 */
async function runDropAll(): Promise<void> {
  console.log('\n' + '='.repeat(70))
  console.log('⚠️  WARNING: DROP ALL DATABASE OBJECTS')
  console.log('='.repeat(70))
  console.log('   This will DELETE ALL DATA in your database!')
  console.log('')

  // 사용자 확인
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  })

  const answer = await new Promise<string>(resolve => {
    readline.question('   Type "YES" to confirm: ', resolve)
  })
  readline.close()

  if (answer !== 'YES') {
    console.log('\n❌ Cancelled.\n')
    process.exit(0)
  }

  const client = new Client({ connectionString: DATABASE_URL })

  try {
    await client.connect()
    console.log('\n🔌 Connected to database')

    const dropAllPath = join(process.cwd(), 'supabase', 'migrations', '00000_drop_all.sql')
    await executeSqlFile(client, dropAllPath)

    console.log('\n✅ Database reset complete!\n')
  } finally {
    await client.end()
  }
}

/**
 * Admin 사용자 설정
 */
async function runCreateAdmin(): Promise<void> {
  const client = new Client({ connectionString: DATABASE_URL })

  try {
    await client.connect()
    console.log('\n🔌 Connected to database')

    const adminPath = join(process.cwd(), 'supabase', 'migrations', '20240105_create_admin.sql')
    await executeSqlFile(client, adminPath)

    console.log('\n✅ Admin setup complete!\n')
  } finally {
    await client.end()
  }
}

// CLI 실행
const args = process.argv.slice(2)

if (args.includes('--drop-all')) {
  runDropAll().catch(error => {
    console.error('\n❌ Error:', error.message)
    process.exit(1)
  })
} else if (args.includes('--create-admin')) {
  runCreateAdmin().catch(error => {
    console.error('\n❌ Error:', error.message)
    process.exit(1)
  })
} else {
  runAllMigrations().catch(error => {
    console.error('\n❌ Migration failed:', error.message)
    process.exit(1)
  })
}
