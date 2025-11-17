"use client";

interface HeaderProps {
  darkMode: boolean;
  setDarkMode: (value: boolean | ((prev: boolean) => boolean)) => void;
  urlStatus: "loading" | "success" | "error" | null;
  recipeUrl: string | null;
}

export default function Header({ darkMode, setDarkMode, urlStatus, recipeUrl }: HeaderProps) {
  return (
    <>
      <div className="w-full flex items-center justify-center mb-8 relative">
        {/* Recipe status icon */}
        {urlStatus === "success" && recipeUrl ? (
          <a
            href={recipeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="status-indicator success"
          >
            {/* Journal icon - https://icons.getbootstrap.com/icons/journal-bookmark/ */}
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="white" className="bi bi-journal-bookmark" viewBox="0 0 16 16">
              <path fillRule="evenodd" d="M6 8V1h1v6.117L8.743 6.07a.5.5 0 0 1 .514 0L11 7.117V1h1v7a.5.5 0 0 1-.757.429L9 7.083 6.757 8.43A.5.5 0 0 1 6 8"/>
              <path d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-1h1v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v1H1V2a2 2 0 0 1 2-2"/>
              <path d="M1 5v-.5a.5.5 0 0 1 1 0V5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0V8h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1z"/>
            </svg>
          </a>
        ) : (
          <div
            className={`status-indicator ${
              urlStatus === "loading"
                ? "loading"
                : urlStatus === "error"
                ? "error"
                : "neutral"
            }`}
          >
            {/* Journal icon - https://icons.getbootstrap.com/icons/journal-bookmark/ */}
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="white" className="bi bi-journal-bookmark" viewBox="0 0 16 16">
              <path fillRule="evenodd" d="M6 8V1h1v6.117L8.743 6.07a.5.5 0 0 1 .514 0L11 7.117V1h1v7a.5.5 0 0 1-.757.429L9 7.083 6.757 8.43A.5.5 0 0 1 6 8"/>
              <path d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-1h1v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v1H1V2a2 2 0 0 1 2-2"/>
              <path d="M1 5v-.5a.5.5 0 0 1 1 0V5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0V8h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1z"/>
            </svg>
          </div>
        )}
        <h1 className={`text-center text-4xl font-bold tracking-tight text-primary ${darkMode ? "dark" : "light"}`}>
          Welcome to{" "}
          <span className="brand-badge">
            CookBaum
          </span>
        </h1>
        {/* Toggle dark mode */}
        <button
          onClick={() => setDarkMode((dm) => !dm)}
          className={`dark-mode-toggle ${darkMode ? "dark" : "light"}`}
          type="button"
        >
          {darkMode ? (
            // Sun icon
            // https://icons.getbootstrap.com/icons/sun-fill/
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#FB923C" className="bi bi-sun-fill" viewBox="0 0 16 16">
              <path d="M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8M8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0m0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13m8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5M3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8m10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0m-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0m9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707M4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708"/>
            </svg>
          ) : (
            // Moon icon
            // https://icons.getbootstrap.com/icons/moon-fill/
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#FB923C" className="bi bi-moon-fill" viewBox="0 0 16 16">
              <path d="M6 .278a.77.77 0 0 1 .08.858 7.2 7.2 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277q.792-.001 1.533-.16a.79.79 0 0 1 .81.316.73.73 0 0 1-.031.893A8.35 8.35 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.75.75 0 0 1 6 .278"/>
            </svg>
          )}
        </button>
      </div>
      {/* Divider between header and chat history */}
      <div className={`divider mb-4 ${darkMode ? "dark" : "light"}`}></div>
    </>
  );
}

