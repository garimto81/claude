/**
 * Supabase 마이그레이션 실행 스크립트
 *
 * Supabase CLI 없이 직접 원격 DB에 SQL을 실행합니다.
 * Service Role Key를 사용하여 Admin 권한으로 실행됩니다.
 */

import { createClient } from '@supabase/supabase-js'
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'

// 환경 변수 로드
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Missing environment variables!')
  console.error('   NEXT_PUBLIC_SUPABASE_URL:', SUPABASE_URL ? '✓' : '✗')
  console.error('   SUPABASE_SERVICE_ROLE_KEY:', SUPABASE_SERVICE_ROLE_KEY ? '✓' : '✗')
  process.exit(1)
}

// Supabase Admin Client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
})

/**
 * SQL 파일을 실행합니다.
 */
async function executeSqlFile(filePath: string): Promise<void> {
  const fileName = filePath.split(/[/\\]/).pop()!
  console.log(`\n📄 Executing: ${fileName}`)

  try {
    const sql = readFileSync(filePath, 'utf-8')

    // Supabase RPC를 통해 SQL 실행
    // Note: Supabase JS client는 raw SQL 실행을 직접 지원하지 않으므로
    // PostgreSQL function을 통해 실행합니다.
    const { data, error } = await supabase.rpc('exec_sql', { sql_query: sql })

    if (error) {
      // exec_sql 함수가 없으면 생성
      if (error.message.includes('function') && error.message.includes('does not exist')) {
        console.log('   Creating exec_sql function...')
        await createExecSqlFunction()

        // 다시 시도
        const { data: retryData, error: retryError } = await supabase.rpc('exec_sql', { sql_query: sql })

        if (retryError) {
          throw retryError
        }

        console.log(`   ✅ ${fileName} executed successfully`)
        return
      }

      throw error
    }

    console.log(`   ✅ ${fileName} executed successfully`)
  } catch (error: any) {
    console.error(`   ❌ Error in ${fileName}:`)
    console.error(`      ${error.message}`)
    throw error
  }
}

/**
 * exec_sql helper function 생성
 */
async function createExecSqlFunction(): Promise<void> {
  const createFunctionSql = `
    CREATE OR REPLACE FUNCTION exec_sql(sql_query TEXT)
    RETURNS VOID AS $$
    BEGIN
      EXECUTE sql_query;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
  `

  // 이 함수는 Supabase 대시보드에서 수동으로 생성해야 합니다.
  console.warn('⚠️  exec_sql function not found.')
  console.warn('   Please run this SQL in Supabase Dashboard SQL Editor:')
  console.warn('')
  console.warn(createFunctionSql)
  console.warn('')

  throw new Error('exec_sql function required. See message above.')
}

/**
 * 모든 마이그레이션을 순서대로 실행합니다.
 */
async function runAllMigrations(): Promise<void> {
  const migrationsDir = join(process.cwd(), 'supabase', 'migrations')

  console.log('🚀 Starting Supabase Migrations')
  console.log('   Project URL:', SUPABASE_URL)
  console.log('   Migrations Dir:', migrationsDir)

  // 마이그레이션 파일 목록 (순서대로)
  const migrationFiles = readdirSync(migrationsDir)
    .filter(file => file.endsWith('.sql'))
    .sort()

  console.log(`\n   Found ${migrationFiles.length} migration files:\n`)

  let executedCount = 0
  let failedCount = 0

  for (const file of migrationFiles) {
    const filePath = join(migrationsDir, file)

    // 00000_drop_all.sql은 건너뛰기 (명시적으로 실행해야 함)
    if (file.includes('drop_all')) {
      console.log(`\n⏭️  Skipping: ${file}`)
      console.log('   (Run this manually if you need to reset the database)')
      continue
    }

    try {
      await executeSqlFile(filePath)
      executedCount++
    } catch (error) {
      failedCount++
      console.error(`\n❌ Failed to execute ${file}`)

      // 치명적인 에러면 중단
      if (file.includes('create_profiles') || file.includes('create_trigger')) {
        console.error('\n🛑 Critical migration failed. Stopping.')
        process.exit(1)
      }

      console.log('   Continuing with next migration...\n')
    }
  }

  console.log('\n' + '='.repeat(60))
  console.log(`✅ Migrations Complete`)
  console.log(`   Executed: ${executedCount}`)
  console.log(`   Failed: ${failedCount}`)
  console.log(`   Skipped: ${migrationFiles.length - executedCount - failedCount}`)
  console.log('='.repeat(60))
}

/**
 * 특정 마이그레이션만 실행합니다.
 */
async function runSpecificMigration(fileName: string): Promise<void> {
  const migrationsDir = join(process.cwd(), 'supabase', 'migrations')
  const filePath = join(migrationsDir, fileName)

  console.log(`🚀 Running specific migration: ${fileName}`)

  await executeSqlFile(filePath)

  console.log('\n✅ Migration complete!')
}

// CLI 실행
const args = process.argv.slice(2)

if (args.length === 0) {
  // 모든 마이그레이션 실행
  runAllMigrations().catch(error => {
    console.error('\n❌ Migration failed:', error.message)
    process.exit(1)
  })
} else {
  // 특정 마이그레이션 실행
  const fileName = args[0]
  runSpecificMigration(fileName).catch(error => {
    console.error('\n❌ Migration failed:', error.message)
    process.exit(1)
  })
}
