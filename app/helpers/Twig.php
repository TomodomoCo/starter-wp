<?php

namespace Tomodomo\Helpers;

use Pimple\Container;
use Timber;

class Twig
{
    /**
     * @param Container
     *
     * @return void
     */
    public function __construct(Container $container) : void
    {
        $this->container = $container;

        return;
    }

    /**
     * Compile a template
     *
     * @param string|array $template
     * @param array $context
     *
     * @return string
     */
    public function compile($template, array $context = []) : string
    {
        // Build the context settings
        $settings = array_merge(
            $context,
            $this->container['context']
        );

        // Make sure template an array
        $template = is_array($template) ? $template : [$template];

        return Timber::compile($template, $settings);
    }
}
