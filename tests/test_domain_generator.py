"""
Tests for domain generator functionality.
"""

import pytest

from domaingenchecker.config import GeneratorConfig
from domaingenchecker.domain_generator import DomainGenerator


class TestDomainGenerator:
    """Test cases for DomainGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig()
        self.tlds = {"com", "net", "org"}
        self.generator = DomainGenerator(self.config, self.tlds)

    def test_clean_domain(self):
        """Test domain cleaning functionality."""
        test_cases = [
            ("example.com", "example.com"),
            ("EXAMPLE.COM", "example.com"),
            ("www.example.com", "example.com"),
            ("http://example.com", "example.com"),
            ("https://www.example.com", "example.com"),
            ("  example.com  ", "example.com"),
        ]

        for input_domain, expected in test_cases:
            result = self.generator._clean_domain(input_domain)
            assert result == expected, f"Failed for {input_domain}"

    def test_is_valid_domain_name(self):
        """Test domain name validation."""
        valid_domains = [
            "example.com",
            "sub.example.com",
            "test-domain.org",
            "a.co",
        ]

        invalid_domains = [
            "",
            "invalid",
            "a" * 254,  # Too long
            "-invalid.com",  # Starts with hyphen
            "invalid-.com",  # Ends with hyphen
            ".com",  # Missing domain
        ]

        for domain in valid_domains:
            assert self.generator._is_valid_domain_name(
                domain
            ), f"Should be valid: {domain}"

        for domain in invalid_domains:
            assert not self.generator._is_valid_domain_name(
                domain
            ), f"Should be invalid: {domain}"

    def test_generate_omission_variants(self):
        """Test character omission variants."""
        domain = "test"
        variants = list(self.generator._generate_omission_variants(domain))

        expected = ["est", "tst", "tet", "tes"]
        assert sorted(variants) == sorted(expected)

    def test_generate_repetition_variants(self):
        """Test character repetition variants."""
        domain = "test"
        variants = list(self.generator._generate_repetition_variants(domain))

        # Should include doubled characters
        assert "ttest" in variants  # Double first char
        assert "teest" in variants  # Double second char
        assert "tesst" in variants  # Double third char
        assert "testt" in variants  # Double last char

    def test_generate_keyboard_variants(self):
        """Test keyboard-based typo variants."""
        domain = "test"
        variants = list(self.generator._generate_keyboard_variants(domain))

        # 't' adjacent to 'r', 'y', 'g' on QWERTY
        assert any("r" in variant for variant in variants)
        assert any("y" in variant for variant in variants)

    def test_generate_domain_variations(self):
        """Test complete domain variation generation."""
        # Limit variants for testing
        self.config.max_variants_per_domain = 10

        domain = "test.com"
        variations = list(self.generator.generate_domain_variations(domain))

        # Should generate some variants
        assert len(variations) > 0
        assert len(variations) <= self.config.max_variants_per_domain

        # All variations should be valid domains
        for variant in variations:
            assert self.generator._is_valid_domain_name(variant)
            # Should not be the original domain
            assert variant != domain

    def test_disabled_techniques(self):
        """Test that disabled techniques don't generate variants."""
        # Disable all techniques
        config = GeneratorConfig(
            max_variants_per_domain=50,
            enable_keyboard_typos=False,
            enable_visual_similarity=False,
            enable_character_omission=False,
            enable_character_repetition=False,
            enable_character_substitution=False,
            enable_subdomain_variations=False,
            enable_idn_confusables=False,
        )

        generator = DomainGenerator(config, self.tlds)
        variations = list(generator.generate_domain_variations("test.com"))

        # Should generate no variations when all techniques disabled
        assert len(variations) == 0

    def test_subdomain_variations(self):
        """Test subdomain variation generation."""
        domain = "test"
        variants = list(self.generator._generate_subdomain_variants(domain))

        # Should include common patterns
        assert "www-test" in variants
        assert "mail-test" in variants
        assert "test-www" in variants
        assert "wwwtest" in variants
