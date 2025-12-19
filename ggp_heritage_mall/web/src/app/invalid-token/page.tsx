import Link from "next/link";

export default function InvalidTokenPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-background)]">
      <div className="max-w-md w-full mx-4 text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 mb-6">
            <svg
              className="w-10 h-10 text-red-500"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-3xl font-serif text-white mb-4">
            유효하지 않은 초대 토큰
          </h1>
          <p className="text-gray-400 mb-8">
            제공된 초대 토큰이 유효하지 않거나 만료되었습니다.
            <br />
            GGP Heritage Mall은 초대 전용 쇼핑몰입니다.
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-[var(--color-surface)] rounded-lg p-6 text-left">
            <h2 className="text-lg font-semibold text-white mb-3">
              초대 토큰을 받는 방법
            </h2>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-[var(--color-gold)] mr-2 flex-shrink-0 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>GG POKER VIP 등급을 획득하세요</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-[var(--color-gold)] mr-2 flex-shrink-0 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>이메일로 발송된 초대 링크를 확인하세요</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-[var(--color-gold)] mr-2 flex-shrink-0 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>또는 QR 코드로 가입 후 승인을 기다리세요</span>
              </li>
            </ul>
          </div>

          <Link
            href="/"
            className="inline-block w-full bg-[var(--color-gold)] text-black font-semibold py-3 px-6 rounded-lg hover:bg-[var(--color-gold)]/90 transition-colors"
          >
            홈으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
