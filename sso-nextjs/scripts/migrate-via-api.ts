/**
 * Supabase API를 통한 마이그레이션 실행
 *
 * PostgreSQL 직접 연결 대신 Supabase REST API 사용
 */

import { createClient } from '@supabase/supabase-js'
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'
import * as dotenv from 'dotenv'

// 환경 변수 로드
dotenv.config({ path: '.env.local' })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Missing environment variables!')
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
 * SQL 문을 실행합니다 (Supabase Management API 사용)
 */
async function executeSql(sql: string, fileName: string): Promise<void> {
  console.log(`\n📄 Executing: ${fileName}`)

  try {
    // Supabase Management API는 직접 SQL 실행을 지원하지 않으므로
    // 대신 각 테이블/함수를 개별적으로 생성해야 합니다.

    // 하지만 더 간단한 방법은 Dashboard에서 수동 실행하는 것입니다.
    console.log(`   ⚠️  Supabase API does not support raw SQL execution.`)
    console.log(`   ℹ️  Please run this SQL manually in Supabase Dashboard:`)
    console.log(`   📋 ${SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}/sql`)

    return
  } catch (error: any) {
    console.error(`   ❌ Error: ${error.message}`)
    throw error
  }
}

/**
 * 마이그레이션 파일을 출력합니다
 */
async function printMigrations(): Promise<void> {
  const migrationsDir = join(process.cwd(), 'supabase', 'migrations')

  console.log('\n' + '='.repeat(70))
  console.log('📋 SUPABASE MIGRATION SQL')
  console.log('='.repeat(70))
  console.log('\nℹ️  Copy-paste each SQL section into Supabase Dashboard:')
  console.log(`   ${SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}/sql`)
  console.log('='.repeat(70))

  // 마이그레이션 파일 목록
  const migrationFiles = readdirSync(migrationsDir)
    .filter(file => file.endsWith('.sql'))
    .sort()

  migrationFiles.forEach((file, index) => {
    const filePath = join(migrationsDir, file)
    const content = readFileSync(filePath, 'utf-8')

    // drop_all과 create_admin은 스킵
    if (file.includes('drop_all')) {
      console.log(`\n\n${'#'.repeat(70)}`)
      console.log(`# [SKIP] ${file}`)
      console.log(`#`.repeat(70))
      console.log('⏭️  Run this manually only if you need to reset database')
      return
    }

    if (file.includes('create_admin')) {
      console.log(`\n\n${'#'.repeat(70)}`)
      console.log(`# [LATER] ${file}`)
      console.log(`#`.repeat(70))
      console.log('⏭️  Run this AFTER creating users in Dashboard')
      return
    }

    console.log(`\n\n${'#'.repeat(70)}`)
    console.log(`# [${index + 1}] ${file}`)
    console.log(`${'#'.repeat(70)}`)
    console.log('\n--- COPY BELOW SQL ---\n')
    console.log(content)
    console.log('\n--- END ---')
  })

  console.log('\n\n' + '='.repeat(70))
  console.log('✅ All SQL displayed.')
  console.log('='.repeat(70))
  console.log('\n📝 Next steps:')
  console.log('   1. Go to: Supabase Dashboard → SQL Editor')
  console.log('   2. Copy each SQL section above')
  console.log('   3. Run in order (1, 2, 3, 4)')
  console.log('   4. Create admin@example.com in Dashboard')
  console.log('   5. Run migration [LATER] to set admin role')
  console.log('')
}

// 실행
printMigrations().catch(error => {
  console.error('❌ Error:', error.message)
  process.exit(1)
})
