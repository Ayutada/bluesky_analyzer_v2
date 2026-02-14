import { useState, useEffect, useRef } from 'react';

const AutocompleteInput = ({ value, onChange, placeholder, disabled }) => {
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [searchLoading, setSearchLoading] = useState(false);
    const dropdownRef = useRef(null);

    // Debounce logic
    useEffect(() => {
        const timer = setTimeout(() => {
            // Only search if value is not empty and we are looking for suggestions
            // However, typical autocomplete searches as you type.
            // We need to differentiate between "user typed" and "user selected".
            // But for simplicity, we search whatever is in the box if it's longer than 2 chars
            // and if the dropdown isn't explicitly closed (logic handled by blur/selection).
            if (value && value.length >= 2) {
                fetchSuggestions(value);
            } else {
                setSuggestions([]);
            }
        }, 300); // 300ms debounce

        return () => clearTimeout(timer);
    }, [value]);

    // Click outside to close
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowSuggestions(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const fetchSuggestions = async (query) => {
        // If the query matches a "selected" state (e.g. exactly one of the previous suggestions), 
        // we might want to avoid re-fetching, but usually it's fine.

        setSearchLoading(true);
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const data = await response.json();
                setSuggestions(data);
                setShowSuggestions(true);
            }
        } catch (error) {
            console.error("Search error:", error);
        } finally {
            setSearchLoading(false);
        }
    };

    const handleSelect = (actor) => {
        onChange(actor.handle);
        setShowSuggestions(false);
    };

    const handleInputChange = (e) => {
        onChange(e.target.value);
        // Re-open suggestions if user types again
        if (!showSuggestions) setShowSuggestions(true);
    };

    return (
        <div className="autocomplete-wrapper" ref={dropdownRef}>
            <input
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={handleInputChange}
                onFocus={() => value && value.length >= 2 && setShowSuggestions(true)}
                disabled={disabled}
            />

            {showSuggestions && suggestions.length > 0 && (
                <div className="autocomplete-dropdown">
                    {suggestions.map((actor) => (
                        <div
                            key={actor.did}
                            className="autocomplete-item"
                            onClick={() => handleSelect(actor)}
                        >
                            <img
                                src={actor.avatar || `https://ui-avatars.com/api/?name=${actor.handle}`}
                                alt="avatar"
                                className="autocomplete-avatar"
                            />
                            <div className="autocomplete-info">
                                <span className="autocomplete-name">{actor.displayName || actor.handle}</span>
                                <span className="autocomplete-handle">@{actor.handle}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AutocompleteInput;
